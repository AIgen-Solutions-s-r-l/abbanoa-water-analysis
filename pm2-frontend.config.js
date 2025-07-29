module.exports = {
  apps: [{
    name: 'abbanoa-frontend',
    script: 'npm',
    args: 'run dev:prod',
    cwd: './frontend',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      PORT: '8502',
      BACKEND_URL: 'http://localhost:8000'
    },
    error_file: './logs/frontend-error.log',
    out_file: './logs/frontend-out.log',
    log_file: './logs/frontend-combined.log',
    time: true
  }]
}; 