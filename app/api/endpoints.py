# import asyncio
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import json
from app.models.comparison_manager import ComparisonManager
from app.services.structured_openai_service import call_openai_api_structured
import os

router = APIRouter()
logger = logging.getLogger(__name__)


# Initialize the comparison manager
comparison_manager = ComparisonManager()


@router.websocket("/ws/compare")
async def websocket_compare(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        # Receive the initial request data
        raw_data = await websocket.receive_json()

        # Debug log the received data
        logger.info("Received WebSocket data:")
        logger.info(f"Raw data: {raw_data}")

        if not isinstance(raw_data, dict):
            await comparison_manager.send_status(
                websocket,
                "error",
                "Invalid request format"
            )
            return

        urls = {
            'url1': raw_data['urls']['url1'].strip(),
            'url2': raw_data['urls']['url2'].strip()
        }
        user_input = raw_data.get('user_input')

        # Debug log the extracted URLs
        logger.info(f"Extracted URLs: {urls}")

        if not urls or not user_input:
            await comparison_manager.send_status(
                websocket,
                "error",
                "Missing required fields in request"
            )
            return

        # Start the comparison process
        await comparison_manager.start_comparison(websocket, urls, user_input)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        await comparison_manager.handle_client_disconnect(websocket)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        await comparison_manager.send_status(
            websocket,
            "error",
            "Invalid JSON format"
        )
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
        await comparison_manager.send_status(
            websocket,
            "error",
            str(e)
        )

@router.websocket("/ws/compare/structured")
async def websocket_structured_compare(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        # Receive the initial request data
        raw_data = await websocket.receive_json()

        # Debug log the received data
        logger.info("Received WebSocket data:")
        logger.info(f"Raw data: {raw_data}")

        if not isinstance(raw_data, dict):
            await comparison_manager.send_status(
                websocket,
                "error",
                "Invalid request format"
            )
            return

        urls = {
            'url1': raw_data['urls']['url1'].strip(),
            'url2': raw_data['urls']['url2'].strip()
        }
        user_input = raw_data.get('user_input')

        # Debug log the extracted URLs
        logger.info(f"Extracted URLs: {urls}")

        if not urls or not user_input:
            await comparison_manager.send_status(
                websocket,
                "error",
                "Missing required fields in request"
            )
            return

        # Start the comparison process
        await comparison_manager.start_structured_comparison(websocket, urls, user_input)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        await comparison_manager.handle_client_disconnect(websocket)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        await comparison_manager.send_status(
            websocket,
            "error",
            "Invalid JSON format"
        )
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
        await comparison_manager.send_status(
            websocket,
            "error",
            str(e)
        )


@router.post("/openai-test")
async def test_openai():
    """ Creates a simple prompt to OpenAI to verify we can use API successfully. """
    try:        
        # do we have an OpenAI API key?
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=400, detail="OpenAI API Key not found")
        else:
            return {"message": call_openai_api_structured("Which is better, apples or oranges?")}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
