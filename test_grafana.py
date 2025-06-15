import requests
import re

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MDAxNzUzOSwidG9rZW5fdmVyc2lvbiI6M30.Hei9NylR0uqrF4QihxY7Ww0pNSSP_PiVVUecMHWXkXg"
HOST = "http://localhost:8001"

# Pattern pour vérifier les expressions Prometheus
prometheus_pattern = re.compile(r'\\o\\-\\s')  # Corrigé: \\o\\-\\s

# Pattern pour vérifier les labels
label_pattern = re.compile(r'\\o\\-\\s')  # Corrigé: \\o\\-\\s


def test_match():
    files = {"file": open("data/oversampled_gravures/---e/symbole_20250320_141159_aug_2.jpg", "rb")}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.post(f"{HOST}/match", files=files, headers=headers)
    print("/match:", r.status_code, r.json())


def test_embedding():
    files = {"file": open("data/oversampled_gravures/---e/symbole_20250320_141159_aug_2.jpg", "rb")}
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.post(f"{HOST}/embedding", files=files, headers=headers)
    print("/embedding:", r.status_code, r.json())


def test_search_tags():
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    r = requests.post(f"{HOST}/search_tags", json=["triangle"], headers=headers)
    print("/search_tags:", r.status_code, r.json())


def test_verre():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.get(f"{HOST}/verre/12", headers=headers)
    print("/verre/1:", r.status_code, r.json())


# Appelle les fonctions
test_match()
test_embedding()
test_search_tags()
test_verre()
