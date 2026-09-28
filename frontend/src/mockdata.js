export const mockResponse = {
  suggestion:
    "This looks like a connection pool exhaustion on payments-service. Restart the service and increase the max pool size.",
  steps: [
    "Check active DB connections on payments-service",
    "Restart the payments-service pods",
    "Increase DB_POOL_MAX from 20 to 50",
    "Monitor error rate for 15 minutes",
  ],
  recalledIncidents: [
    {
      id: "INC-1042",
      service: "payments-service",
      date: "3 weeks ago",
      rootCause: "DB connection pool exhausted during a traffic spike",
      resolution: "Increased pool size and restarted pods",
      timeToResolve: "18 min",
    },
    {
      id: "INC-0987",
      service: "orders-service",
      date: "2 months ago",
      rootCause: "Connection leak after a bad deploy",
      resolution: "Rolled back deploy, then patched the leak",
      timeToResolve: "35 min",
    },
  ],
};