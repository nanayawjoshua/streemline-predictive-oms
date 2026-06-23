ARG GO_VERSION=1.22

FROM golang:${GO_VERSION} AS builder
WORKDIR /build
COPY go.mod .
COPY main.go .
RUN CGO_ENABLED=0 go build -o connector .

FROM alpine:3.20
RUN apk --no-cache add ca-certificates
COPY --from=builder /build/connector /connector
EXPOSE 8002
CMD ["/connector"]
