module.exports = {
  apps: [
    {
      name: 'abbanoa-backend',
      script: 'poetry',
      args: 'run uvicorn presentation.api.app_postgres:app --host 0.0.0.0 --port 8000',
      cwd: './src',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PYTHONUNBUFFERED: '1'
      },
      env_production: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-abbanoa-backend-error.log',
      out_file: './logs/pm2-abbanoa-backend-out.log',
      log_file: './logs/pm2-abbanoa-backend-combined.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      // Restart delay
      restart_delay: 4000,
      // Max restart attempts
      max_restarts: 10,
      min_uptime: '10s',
      // Grace period for shutdown
      kill_timeout: 5000,
      // Wait before considering app as ready
      wait_ready: true,
      listen_timeout: 10000
    },
    {
      name: 'abbanoa-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: './frontend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 3000
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/pm2-abbanoa-frontend-error.log',
      out_file: './logs/pm2-abbanoa-frontend-out.log',
      log_file: './logs/pm2-abbanoa-frontend-combined.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000
    }
  ]
}; 