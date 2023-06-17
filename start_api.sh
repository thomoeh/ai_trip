export openai_api_key=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

# Debug?
export DEBUG=False
echo Debug: $DEBUG

# Set the port numbers
ngrok_port=8000
uvicorn_port=8000
# Allow 10 minutes of inactivity before shutting down the server, since OpenAI queries can take very long:
n_seconds_idle_allowed=6000


echo "Starting ngrok"
# This command starts ngrok in the background and redirects the ngrok output to /dev/null, which discards it.
/home/azureuser/cloudfiles/code/Users/valdimar/ragpt4/ai_trip/ngrok http --region=us  - "$ngrok_port" > /dev/null &

# Wait until ngrok tunnel is available
while [[ -z "$ngrok_tunnel" || "$ngrok_tunnel" == "null" ]]; do
    echo "Waiting for ngrok tunnel..."
    sleep 1.5
    ngrok_tunnel=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
done

echo "Starting uvicorn server..."
# Start the API
uvicorn main:app --host 0.0.0.0 --port "$uvicorn_port"  --timeout-keep-alive "$n_seconds_idle_allowed" --log-config logging_config.ini > server_logs.txt 2>&1 &

#uvicorn main:app --host 0.0.0.0 --port "$uvicorn_port" --log-config logging_config.ini > server_logs.txt 2> >(tee -a server_logs.txt >&2) &
#uvicorn main:app --host 0.0.0.0 --port "$uvicorn_port" --log-config logging_config.ini > server_logs.txt 2> >(tee -a server_logs.txt >&1) &
#uvicorn main:app --host 0.0.0.0 --port "$uvicorn_port" --log-config logging_config.ini > >(tee -a server_logs.txt) 2> >(tee -a server_logs.txt >&2) &



UVICORN_PID=$!


# Wait until uvicorn server is ready
while ! curl -s "http://localhost:$uvicorn_port" > /dev/null; do
    # Check if the process is still running
    if ! ps -p $UVICORN_PID > /dev/null; then
        echo "Uvicorn process has stopped. Exiting..."
        echo "The last few lines of the server logs are:"
        tail server_logs.txt
        exit 1
    fi
    echo "Waiting for uvicorn server..."
    sleep 4
done

echo "Uvicorn server has been started!"


echo "ngrok tunnel available at $ngrok_tunnel"