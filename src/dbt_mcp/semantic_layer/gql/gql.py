GRAPHQL_QUERIES = {
    "dimensions": """
query GetDimensions($environmentId: BigInt!, $metrics: [MetricInput!]!) {
  dimensions(environmentId: $environmentId, metrics: $metrics) {
    description
    name
    type
    queryableGranularities
    queryableTimeGranularities
  }
}
    """,
    "entities": """
query GetEntities($environmentId: BigInt!, $metrics: [MetricInput!]!) {
  entities(environmentId: $environmentId, metrics: $metrics) {
    description
    name
    type
  }
}
    """,
}
