# Troubleshooting EC2 Ubuntu Python 3.11 Flask App Deployment

This document compiles the troubleshooting steps and solutions encountered while deploying a Flask application with Python 3.11, Gunicorn, and Nginx on an Ubuntu 22.04 EC2 instance.

-----

## 1\. Initial Python 3.11 Setup

**Problem:** Ubuntu 22.04 defaults to Python 3.10, but the project requires Python 3.11.

**Solution:** Install Python 3.11 via the `deadsnakes` PPA.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv # python3.11-venv is crucial for virtual environments
```

**Key Takeaway:** Always install the `*-venv` package for the specific Python version you intend to use for virtual environments on Debian/Ubuntu systems.

-----

## 2\. Virtual Environment Creation Failure

**Problem:** `venv` creation failed with "ensurepip is not available" error.

**Error Message:**

```
The virtual environment was not created successfully because ensurepip is not
available. On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command. apt install python3.10-venv
```

**Solution:** Install the `python3.11-venv` package, as the project specifically uses Python 3.11.

```bash
sudo apt update
sudo apt install python3.11-venv
```

**Then, recreate the virtual environment:**

```bash
cd /path/to/your/project
python3.11 -m venv .venv
```

**Key Takeaway:** The `venv` module relies on a corresponding `*-venv` package for the specific Python version.

-----

## 3\. Systemd Service Configuration for Gunicorn

**Goal:** Create a systemd service to run the Flask app with Gunicorn.

**Initial Service File (Problematic):**

```ini
# /etc/systemd/system/3mtt-chatbot.service (initial sudo tee content)
[Unit]
Description=3MTT Chatbot Flask App
After=network.target

[Service]
User=ec2-user # Or ubuntu
WorkingDirectory=/home/ec2-user/3mtt-chatbot
EnvironmentFile=/home/ec2-user/3mtt-chatbot/.env # If used
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Problem:** `ExecStart` initially pointed to `/usr/local/bin/gunicorn`.

**Solution:** Change `ExecStart` to point to the Gunicorn executable *inside the virtual environment*.

```ini
ExecStart=/home/ubuntu/test-chat-bot/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
```

**Problem:** `systemctl edit` resulted in "more than one ExecStart= setting" and "bad unit file setting" errors.

**Error Message:**

```
3mtt-chatbot.service: Service has more than one ExecStart= setting, which is o>
Loaded: bad-setting (Reason: Unit 3mtt-chatbot.service has a bad unit file setting.)
Main PID: 6788 (code=exited, status=203/EXEC)
```

**Reason:** The `sudo tee` command created a complete service file, and `sudo systemctl edit` created an `override.conf` which also included an `ExecStart`, causing a conflict.

**Solution:**

1.  **Stop and disable the service:**

    ```bash
    sudo systemctl stop 3mtt-chatbot.service
    sudo systemctl disable 3mtt-chatbot.service
    ```

2.  **Remove existing service files/overrides:**

    ```bash
    sudo rm -f /etc/systemd/system/3mtt-chatbot.service
    sudo rm -rf /etc/systemd/system/3mtt-chatbot.service.d
    ```

3.  **Perform a full daemon reload:**

    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Create the complete service file using `systemctl edit --full`:** This ensures a single, definitive service file.

    ```bash
    sudo systemctl edit --full 3mtt-chatbot.service
    ```

    Paste the complete, corrected service file content into the editor (including `[Unit]`, `[Service]`, `[Install]` sections).

    ```ini
    [Unit]
    Description=3MTT Chatbot Flask App
    After=network.target

    [Service]
    User=ubuntu # Verify this is your EC2 instance's user (e.g., ec2-user)
    WorkingDirectory=/home/ubuntu/test-chat-bot
    # EnvironmentFile=/home/ubuntu/test-chat-bot/.env # Uncomment if you use a .env file
    ExecStart=/home/ubuntu/test-chat-bot/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
    Restart=always
    StandardOutput=journal
    StandardError=journal
    SyslogIdentifier=3mtt-chatbot

    [Install]
    WantedBy=multi-user.target
    ```

5.  **Reload daemon, enable, and start service:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable 3mtt-chatbot.service
    sudo systemctl start 3mtt-chatbot.service
    sudo systemctl status 3mtt-chatbot.service
    journalctl -u 3mtt-chatbot.service -f
    ```

**Key Takeaway:** Be careful when using `sudo tee` for service files and then `systemctl edit`. `systemctl edit --full` is often the cleanest way to define a service from scratch or completely redefine it.

-----

## 4\. Nginx 502 Bad Gateway Error

**Problem:** After systemd service was running, Nginx returned "502 Bad Gateway".

**Nginx Error Log Snippet:**

```
connect() failed (111: Unknown error) while connecting to upstream, client: ..., server: ..., request: "GET / HTTP/1.1", upstream: "http://127.0.0.1:5002/", host: "..."
```

**Reason:** Error `111` ("Connection refused") indicates that Nginx could not connect to the Gunicorn process. This means Gunicorn was either not running, not listening on the expected address/port, or was crashing immediately.

**Initial Diagnosis & Solution Path:**

1.  **Check Gunicorn Service Status:** `sudo systemctl status 3mtt-chatbot.service`. If not running, proceed to check logs.
2.  **Check Gunicorn Logs:** `journalctl -u 3mtt-chatbot.service -f`. This revealed a `gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>` error.

**Key Takeaway:** "502 Bad Gateway" almost always points to an issue with the backend (Gunicorn/Flask app) rather than Nginx itself. Check the backend service's status and logs first.

-----

## 5\. Gunicorn "Worker failed to boot" Error (Application-Level Error)

**Problem:** Gunicorn was failing to start its workers, leading to the 502.

**Gunicorn Log Snippet:**

```
TypeError: Limiter.__init__() got multiple values for argument 'key_func'
[2025-07-31 12:15:01 +0000] [14771] [INFO] Worker exiting (pid: 14771)
[2025-07-31 12:15:01 +0000] [14770] [ERROR] Worker (pid:14771) exited with code 3
[2025-07-31 12:15:01 +0000] [14770] [ERROR] Shutting down: Master
[2025-07-31 12:15:01 +0000] [14770] [ERROR] Reason: Worker failed to boot.
```

**Reason:** A `TypeError` in the Flask application code, specifically with the `Flask-Limiter` (or `limits`) library. The `key_func` argument was being passed multiple times during `Limiter` initialization, likely due to a syntax mismatch between Flask-Limiter versions.

**Solution:**

1.  **Run Gunicorn manually for verbose output:**

    ```bash
    sudo systemctl stop 3mtt-chatbot.service # Stop service to free port
    cd /home/ubuntu/test-chat-bot
    source .venv/bin/activate
    /home/ubuntu/test-chat-bot/.venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5002 app:app --log-level debug
    ```

    This directly showed the `TypeError`.

2.  **Modify Flask application code (`app.py`):** Correct the `Limiter` initialization to pass `key_func` only once, preferably using `flask_limiter.util.get_remote_address` for robustness with proxies.

    ```python
    from flask import Flask, request
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    app = Flask(__name__)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    # ... rest of your Flask app code ...
    ```

3.  **Restart systemd service:** `sudo systemctl restart 3mtt-chatbot.service`.

**Key Takeaway:** When Gunicorn's workers fail to boot, it's almost always an error in your application's Python code or its dependencies. Running Gunicorn manually (Method 1) with debug logging is the fastest way to get the specific traceback.

-----

## 6\. Nginx Configuration Location and Port Mismatch

**Problem:** Nginx still showed 502 after the Gunicorn app started, and `ls /etc/nginx/sites-available` only showed `default`.

**Reason 1:** Gunicorn was configured to listen on port `5002` (as identified during debugging), but Nginx's `proxy_pass` was still targeting `5000`.
**Reason 2:** The custom Nginx configuration was initially placed in `/etc/nginx/conf.d/3mtt-chatbot.conf` using `sudo tee`, not in `sites-available` with a symlink. Nginx *does* load files from `conf.d` by default (if `nginx.conf` includes it), but the content was outdated or conflicted.

**Solution:**

1.  **Edit the systemd service file** (`sudo systemctl edit 3mtt-chatbot.service`) to change Gunicorn's `--bind` port to `5002`.

    ```ini
    ExecStart=/home/ubuntu/test-chat-bot/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5002 app:app
    ```

2.  **Edit the existing Nginx configuration file in `conf.d`:**

    ```bash
    sudo nano /etc/nginx/conf.d/3mtt-chatbot.conf
    ```

      * Update `server_name` to your EC2 instance's public IP address or domain.
      * Change `proxy_pass http://127.0.0.1:5000;` to `proxy_pass http://127.0.0.1:5002;`.

    <!-- end list -->

    ```nginx
    server {
        listen 80;
        server_name your_ec2_public_ip_or_domain_name; # REPLACE THIS!

        location / {
            proxy_pass http://127.0.0.1:5002; # Changed to 5002
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

3.  **Perform necessary reloads:**

    ```bash
    sudo systemctl daemon-reload       # For systemd service changes
    sudo systemctl restart 3mtt-chatbot.service # For systemd service changes
    sudo nginx -t                      # Test Nginx config syntax
    sudo systemctl reload nginx        # For Nginx config changes
    ```

**Key Takeaway:** Ensure all components (Gunicorn, Nginx `proxy_pass`) are consistently configured to use the correct port. Nginx can load configurations from `conf.d` or `sites-enabled`; ensure consistency and prevent conflicts.

-----

## Final Result: Application Accessible via Nginx

After resolving the `Limiter` `TypeError` and ensuring port consistency between Gunicorn and Nginx, the application became fully accessible via the Nginx proxy.