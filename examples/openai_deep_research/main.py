import os
import random
import string

from openai import OpenAI


def main():
    client = OpenAI()
    prod_environment_id = os.environ.get("DBT_PROD_ENV_ID", os.getenv("DBT_ENV_ID"))
    token = os.environ.get("DBT_TOKEN")
    host = os.environ.get("DBT_HOST", "cloud.getdbt.com")
    input_text = (
        "Determine growth opportunities for a food delivery company in the US."
        + " Use dbt to analyze our data."
    )
    run_id = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    response = client.responses.create(
        model="o3-deep-research",
        input=input_text,
        reasoning={
            "summary": "auto",
        },
        tools=[
            {
                "type": "mcp",
                "server_label": "dbt",
                "server_url": f"https://{host}/api/ai/v1/openai-deep-research/",
                "require_approval": "never",
                "headers": {
                    "Authorization": f"token {token}",
                    "x-dbt-prod-environment-id": prod_environment_id,
                },
            },
        ],
        metadata={"run_id": run_id},
    )
    print(f"Run ID: {run_id}")
    print(f"Output:\n{response.output_text}")


if __name__ == "__main__":
    main()
