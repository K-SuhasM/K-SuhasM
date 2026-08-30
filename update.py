import os
import requests
import xml.etree.ElementTree as ET

USERNAME = os.environ["USER_NAME"]
TOKEN = os.environ["ACCESS_TOKEN"]

API_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

query = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        stargazerCount
      }
    }

    followers {
      totalCount
    }

    contributionsCollection {
      totalCommitContributions
    }
  }
}
"""

response = requests.post(
    API_URL,
    json={
        "query": query,
        "variables": {
            "login": USERNAME
        }
    },
    headers=headers
)

response.raise_for_status()

data = response.json()["data"]["user"]

repositories = data["repositories"]["totalCount"]

stars = sum(
    repo["stargazerCount"]
    for repo in data["repositories"]["nodes"]
)

followers = data["followers"]["totalCount"]

commits = data[
    "contributionsCollection"
]["totalCommitContributions"]


def update_svg(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    values = {
        "repo_data": repositories,
        "commit_data": commits,
        "star_data": stars,
        "follower_data": followers,
        "loc_data": 0
    }

    for element in root.iter():
        element_id = element.attrib.get("id")

        if element_id in values:
            element.text = f"{values[element_id]:,}"

    tree.write(
        filename,
        encoding="unicode"
    )


update_svg("light_mode.svg")
update_svg("dark_mode.svg")

print("Repositories:", repositories)
print("Commits:", commits)
print("Stars:", stars)
print("Followers:", followers)
