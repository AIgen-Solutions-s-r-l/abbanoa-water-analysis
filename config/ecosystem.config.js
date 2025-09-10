module.exports = {
  apps: [
    {
      name: 'abbanoa-frontend',
      cwd: '/root/abbanoa-water-analysis/frontend',
      script: 'npm',
      args: 'run dev',
      env: {
        NODE_ENV: 'development',
        PORT: 3001
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/root/abbanoa-water-analysis/logs/frontend-error.log',
      out_file: '/root/abbanoa-water-analysis/logs/frontend-out.log',
      log_file: '/root/abbanoa-water-analysis/logs/frontend-combined.log',
      time: true
    },
    {
      name: 'abbanoa-postgres-api',
      cwd: '/root/abbanoa-water-analysis',
      script: 'python3',
      args: '-m uvicorn src.presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000',
      env: {
        PYTHONPATH: '/root/abbanoa-water-analysis',
        PORT: 8000
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/root/abbanoa-water-analysis/logs/postgres-api-error.log',
      out_file: '/root/abbanoa-water-analysis/logs/postgres-api-out.log',
      log_file: '/root/abbanoa-water-analysis/logs/postgres-api-combined.log',
      time: true
    }
  ]
}; 