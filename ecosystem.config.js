module.exports = {
  apps: [
    {
      name: 'abbanoa-backend',
      script: '/bin/bash',
      args: '-lc "export PATH=\\"$HOME/.local/bin:$PATH\\"; cd src && poetry run uvicorn presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000"',
      cwd: '/root/abbanoa-water-analysis',
      env: {
        USE_MOCK_API: 'true',
        POSTGRES_HOST: 'localhost',
        POSTGRES_PORT: '5432',
        POSTGRES_DB: 'abbanoa_processing',
        POSTGRES_USER: 'abbanoa_user',
        POSTGRES_PASSWORD: 'abbanoa_dev_pass'
      },
      error_file: 'logs/pm2-backend-error.log',
      out_file: 'logs/pm2-backend-out.log',
      merge_logs: false,
      time: false
    },
    {
      name: 'abbanoa-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: '/root/abbanoa-water-analysis/frontend',
      env: {
        PORT: '3000'
      }
    }
  ]
};