#!/bin/bash

# Configuration
APP_MODULE="main:app"
HOST="0.0.0.0"
PORT="8080"
SSL_KEY="key.pem"
SSL_CERT="cert.pem"
PID_FILE="server.pid"
LOG_FILE="logs/server.log"

# Ensure log directory exists
mkdir -p logs

start() {
    if [ -f "$PID_FILE" ]; then
        if ps -p $(cat $PID_FILE) > /dev/null; then
            echo "Server is already running (PID: $(cat $PID_FILE))"
            return
        else
            echo "PID file exists but process is not running. Removing stale PID file."
            rm $PID_FILE
        fi
    fi

    echo "Starting server..."
    # Check if SSL files exist
    if [ -f "$SSL_KEY" ] && [ -f "$SSL_CERT" ]; then
        nohup uvicorn $APP_MODULE --host $HOST --port $PORT --ssl-keyfile $SSL_KEY --ssl-certfile $SSL_CERT > $LOG_FILE 2>&1 &
    else
        echo "SSL files not found, starting without SSL..."
        nohup uvicorn $APP_MODULE --host $HOST --port $PORT > $LOG_FILE 2>&1 &
    fi
    
    echo $! > $PID_FILE
    echo "Server started with PID $(cat $PID_FILE). Logs: $LOG_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Server is not running (PID file not found)"
        return
    fi

    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill $PID
        # Wait for process to stop
        for i in {1..5}; do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            sleep 1
        done
        
        if ps -p $PID > /dev/null; then
             echo "Force killing server..."
             kill -9 $PID
        fi
    else
        echo "Process $PID not running."
    fi
    
    rm $PID_FILE
    echo "Server stopped."
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "Server is running (PID: $PID)"
        else
            echo "Server is NOT running (Stale PID file found)"
        fi
    else
        echo "Server is NOT running"
    fi
}

restart() {
    stop
    sleep 2
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
