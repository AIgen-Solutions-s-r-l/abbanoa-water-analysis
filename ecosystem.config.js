module.exports = {
  apps: [
    {
      name: 'roccavina-backend',
      script: './run-backend.sh',
      cwd: '.',
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
      error_file: './logs/pm2-roccavina-backend-error.log',
      out_file: './logs/pm2-roccavina-backend-out.log',
      log_file: './logs/pm2-roccavina-backend-combined.log',
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
      name: 'roccavina-frontend',
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
      error_file: './logs/pm2-roccavina-frontend-error.log',
      out_file: './logs/pm2-roccavina-frontend-out.log',
      log_file: './logs/pm2-roccavina-frontend-combined.log',
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