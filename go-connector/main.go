// Go connector — bridges WhatsApp Orchestrator to Prediction Engine.
// Runs alongside the existing bridge_apk orchestrator.
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

type ZoneRiskRequest struct {
	ZoneID           string  `json:"zone_id"`
	Latitude         float64 `json:"latitude"`
	Longitude        float64 `json:"longitude"`
	RecentOutageCnt  int     `json:"recent_outage_count"`
}

type ZoneRiskResponse struct {
	ZoneID     string   `json:"zone_id"`
	RiskScore  float64  `json:"risk_score"`
	RiskLevel  string   `json:"risk_level"`
	WindowHrs  int      `json:"window_hours"`
	Factors    []string `json:"contributing_factors"`
}

type TransformerRiskRequest struct {
	TransformerID string   `json:"transformer_id"`
	ZoneID        string   `json:"zone_id"`
	AssetAgeYears float64  `json:"asset_age_years"`
	LoadPct       float64  `json:"load_percentage"`
	Inspection    *float64 `json:"last_inspection_score,omitempty"`
	OutageCnt     int      `json:"recent_outage_count"`
}

type TransformerRiskResponse struct {
	TransformerID      string  `json:"transformer_id"`
	FailureProb        float64 `json:"failure_probability"`
	RiskLevel          string  `json:"risk_level"`
	DaysToMaintenance  *int    `json:"days_to_maintenance,omitempty"`
}

type DispatchRecommendation struct {
	TransformerID string `json:"transformer_id"`
	Urgency       string `json:"urgency"`
	Reason        string `json:"reason"`
	TeamSize      int    `json:"suggested_team_size"`
}

func main() {
	predictionURL := getEnv("PREDICTION_URL", "http://localhost:8001")
	port := getEnv("CONNECTOR_PORT", "8002")

	http.HandleFunc("/v1/predict/zone", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "POST required", 405)
			return
		}
		var req ZoneRiskRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "bad request", 400)
			return
		}
		resp, err := callZoneRisk(predictionURL, req)
		if err != nil {
			log.Printf("zone risk error: %v", err)
			http.Error(w, "prediction failed", 502)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	log.Printf("Go connector listening on :%s → prediction at %s", port, predictionURL)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func callZoneRisk(base string, req ZoneRiskRequest) (*ZoneRiskResponse, error) {
	body, _ := json.Marshal(req)
	resp, err := http.Post(
		fmt.Sprintf("%s/v1/predict/zone", base),
		"application/json",
		bytes.NewReader(body),
	)
	if err != nil {
		return nil, fmt.Errorf("request: %w", err)
	}
	defer resp.Body.Close()
	var result ZoneRiskResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode: %w", err)
	}
	return &result, nil
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
