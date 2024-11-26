import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from fastapi import FastAPI

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.endpoints import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_websocket_compare():
    with client.websocket_connect("/ws/compare") as websocket:
        test_data = {
            "urls" : {
                "url1" : "https://example.com", 
                "url2" : "https://example2.com"
            },
            "user_input" : {
                "selected_categories" : [],
                "user_preference" : ""
            }
        }
        websocket.send_json(test_data)
        final_response = None
        try:
            while True:
                response = websocket.receive_json()
                assert "status" in response
                if response["status"] == "comparison":
                    final_response = response
                    break
        except WebSocketDisconnect:
            pytest.fail("Failed to receive response from websocket")

        assert final_response is not None
        assert "data" in final_response

def test_websocket_structured_compare():
    """ Test output of structured comparison websocket endpoint """
    with client.websocket_connect("/ws/compare/structured") as websocket:
        test_data = {
            "urls" : {
                "url1" : "https://example.com", 
                "url2" : "https://example2.com"
            },
            "user_input" : {
                "selected_categories" : [],
                "user_preference" : ""
            }
        }
        websocket.send_json(test_data)

        final_response = None
        try:
            while True:
                response = websocket.receive_json() 
                if response["status"] == "comparison":
                    final_response = response
                    break
        except WebSocketDisconnect:
            pytest.fail("WebSocket disconnected unexpectedly")

        assert final_response is not None
        comparison = final_response["data"]
        assert "brief_comparison_title" in comparison
        assert "product1" in comparison
        assert "product2" in comparison
        assert "pros_product1" in comparison
        assert "pros_product2" in comparison
        assert "cons_product1" in comparison
        assert "cons_product2" in comparison
        assert "comparison_summary" in comparison