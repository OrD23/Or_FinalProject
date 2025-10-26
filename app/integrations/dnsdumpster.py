# app/integrations/dnsdumpster.py
import subprocess
import json

def fetch_dnsdumpster_data(target: str) -> dict:
    """
    Call the nmmapper/dnsdumpster tool via subprocess and return normalized results.
    """
    try:
        result = subprocess.run(
            ["python", "dnsdumpster/dnsdumpster.py", "-d", target],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        json_start = output.find("{")
        if json_start == -1:
            raise ValueError("No JSON output found in DNSDumpster response.")
        json_str = output[json_start:]
        data = json.loads(json_str)
        print("dnsdumpster data: ", data)
        return {"dnsdumpster": data}
    except Exception as e:
        return {"dnsdumpster": {"error": str(e)}}
