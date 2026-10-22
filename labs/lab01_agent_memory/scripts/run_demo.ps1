param(
    [string]$TeamId = "team-01",
    [string]$OutputDir = "artifacts/lab01/$TeamId"
)

python -m lab01_agent_memory.demo --team-id $TeamId --output-dir $OutputDir
