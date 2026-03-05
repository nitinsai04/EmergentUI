#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  start.sh — Launch backend + frontend in one command
#  Usage:  ./start.sh
# ─────────────────────────────────────────────────────────────

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/pump-twin-standalone/backend"
FRONTEND="$ROOT/pump-twin-standalone/frontend"

# ── colours ──────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│  Cyber-Resilient Digital Twin — Startup     │${NC}"
echo -e "${CYAN}└─────────────────────────────────────────────┘${NC}"

# ── Backend ──────────────────────────────────────────────────
echo -e "\n${YELLOW}▶ Starting backend  (http://localhost:8002)${NC}"
cd "$BACKEND"
uvicorn app:app --reload --port 8002 &
BACKEND_PID=$!
echo -e "${GREEN}  Backend PID: $BACKEND_PID${NC}"

# ── Frontend ─────────────────────────────────────────────────
echo -e "${YELLOW}▶ Starting frontend (http://localhost:3000)${NC}"
cd "$FRONTEND"
node node_modules/react-scripts/bin/react-scripts.js start &
FRONTEND_PID=$!
echo -e "${GREEN}  Frontend PID: $FRONTEND_PID${NC}"

echo -e "\n${CYAN}Both services running. Press Ctrl+C to stop both.${NC}\n"

# ── Shutdown handler ─────────────────────────────────────────
trap "echo -e '\n${YELLOW}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
