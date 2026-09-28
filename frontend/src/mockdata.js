export const mockResponse = {
  suggestion:
    "This looks like a connection pool exhaustion on payments-service. Restart the service and increase the max pool size.",
  steps: [
    "Check active DB connections on payments-service",
    "Restart the payments-service pods",
    "Increase DB_POOL_MAX from 20 to 50",
    "Monitor error rate for 15 minutes",
  ],
  recalledCount: 2,
};