module.exports = {
  apps: [
    {
      name: 'abbanoa-backend-real',
      script: 'python3',
      args: '-m uvicorn src.presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000',
      cwd: '/root/abbanoa-water-analysis',
      env: {
        POSTGRES_HOST: 'localhost',
        POSTGRES_PORT: '5432',
        POSTGRES_DB: 'abbanoa_processing',
        POSTGRES_USER: 'abbanoa_user',
        POSTGRES_PASSWORD: 'abbanoa_secure_pass',
        USE_MOCK_API: 'false'
      },
      error_file: 'logs/pm2-backend-error.log',
      out_file: 'logs/pm2-backend-out.log',
      merge_logs: false,
      time: false
    }
  ]
};