import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.ping_module.server import app, PingRequest, PingResponse, HostResponse


class TestPingEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("main.async_multiping")
    def test_ping_endpoint(self, mock_async_multiping):
        targets = ["example.com", "google.com"]
        mock_responses = [
            MagicMock(address=target, is_alive=True) for target in targets
        ]
        mock_async_multiping.return_value = mock_responses

        response = self.client.post("/ping/", json={"targets": targets})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["details"]), len(targets))
        self.assertEqual(data["num_of_address"], len(targets))
        self.assertEqual(data["num_of_address_is_alive"], len(targets))
        self.assertEqual(data["num_of_address_not_alive"], 0)

    @patch("main.async_multiping")
    def test_ping_endpoint_failure(self, mock_async_multiping):
        targets = ["example.com", "google.com"]
        mock_async_multiping.side_effect = Exception("Failed to ping")

        response = self.client.post("/ping/", json={"targets": targets})
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Failed to ping")

        
class TestModels(unittest.TestCase):
    def test_ping_request_model(self):
        data = {
            "targets": ["example.com", "google.com"],
            "count": 3,
            "interval": 1.0,
            "timeout": 5.0,
            "concurrent_tasks": 10,
            "source": "192.168.1.1",
            "family": "ipv4",
            "privileged": True
        }
        request = PingRequest(**data)
        self.assertEqual(request.targets, data["targets"])
        self.assertEqual(request.count, data["count"])
        self.assertEqual(request.interval, data["interval"])
        self.assertEqual(request.timeout, data["timeout"])
        self.assertEqual(request.concurrent_tasks, data["concurrent_tasks"])
        self.assertEqual(request.source, data["source"])
        self.assertEqual(request.family, data["family"])
        self.assertEqual(request.privileged, data["privileged"])

    def test_ping_response_model(self):
        data = {
            "execution_time": "2024-04-20 15:30:00",
            "execution_duration": 150.5,
            "num_of_address": 2,
            "num_of_address_is_alive": 1,
            "num_of_address_not_alive": 1,
            "details": [
                {
                    "address": "example.com",
                    "is_alive": True,
                    # Add other fields here as needed
                },
                {
                    "address": "google.com",
                    "is_alive": False,
                    # Add other fields here as needed
                }
            ]
        }
        response = PingResponse(**data)
        self.assertEqual(response.execution_time, data["execution_time"])
        self.assertEqual(response.execution_duration, data["execution_duration"])
        self.assertEqual(response.num_of_address, data["num_of_address"])
        self.assertEqual(response.num_of_address_is_alive, data["num_of_address_is_alive"])
        self.assertEqual(response.num_of_address_not_alive, data["num_of_address_not_alive"])
        self.assertEqual(len(response.details), len(data["details"]))


if __name__ == "__main__":
    unittest.main()

