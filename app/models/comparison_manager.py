import asyncio
import logging
from typing import Optional, Dict, List
from fastapi import WebSocket, HTTPException
from app.services.get_with_selenium import get_with_selenium_async
from app.services.clean_html import clean_html
# from app.services.openai_service import call_openai_api
from app.services.structured_openai_service import call_openai_api_structured
from app.models.product_comparison import ProductComparison
from app.services.prompt_service import create_prompt

logger = logging.getLogger(__name__)


class ComparisonManager:
    '''Manages the comparison process with parallel processing'''
    def __init__(self):
        self.active_tasks: Dict[str, List[asyncio.Task]] = {}
        self._closed_websockets: set[str] = set()
        self._cancelled_tasks: set[str] = set()

    # async def start_comparison(self, websocket: WebSocket, urls: dict, user_input: dict) -> None:
    #     """Manages the comparison process with parallel processing"""
    #     task_id = str(id(websocket))
    #     try:
    #         # Process both URLs concurrently but separately
    #         url1_task = asyncio.create_task(
    #             self.process_single_url(
    #                 websocket,
    #                 urls['url1'],
    #                 1
    #             ),
    #             name=f"URL1-{urls['url1']}"
    #         )
    #         url2_task = asyncio.create_task(
    #             self.process_single_url(
    #                 websocket,
    #                 urls['url2'],
    #                 2
    #             ),
    #             name=f"URL2-{urls['url2']}"
    #         )

    #         self.active_tasks[task_id] = [url1_task, url2_task]

    #         # Wait for both URLs to be processed
    #         results = await asyncio.gather(url1_task, url2_task, return_exceptions=True)

    #         # Check for successful processing
    #         if any(isinstance(r, Exception) for r in results):
    #             error = next(r for r in results if isinstance(r, Exception))
    #             await self.send_status(
    #                 websocket,
    #                 "error",
    #                 f"Error processing URLs: {str(error)}"
    #             )
    #             return

    #         # Generate comparison
    #         try:
    #             logger.info("Generating comparison...")
    #             logger.info(f"Content 1 length: {len(results[0]) if results[0] else 0}")
    #             logger.info(f"Content 2 length: {len(results[1]) if results[1] else 0}")

    #             # Create a prompt for comparison
    #             prompt = create_prompt(
    #                 results[0],
    #                 results[1],
    #                 user_input['selected_categories'],
    #                 user_input['user_preference']
    #             )

    #             # Make call to OpenAI
    #             await self.send_status(websocket, "progress", "Generating comparison...")
    #             comparison = await asyncio.to_thread(call_openai_api, prompt)
    #             await self.send_status(websocket, "comparison", None, comparison)

    #         except Exception as e:
    #             logger.error(f"Error generating comparison: {str(e)}")
    #             await self.send_status(
    #                 websocket,
    #                 "error",
    #                 f"Error generating comparison: {str(e)}"
    #             )
    #     except Exception as e:
    #         logger.error(f"Unexpected error in comparison: {str(e)}")
    #         await self.send_status(
    #             websocket,
    #             "error",
    #             f"Unexpected error: {str(e)}"
    #         )
    #     finally:
    #         self.active_tasks.pop(task_id, None)

    async def start_structured_comparison(self, websocket: WebSocket, urls: dict, user_input: dict) -> None:
        """Manages the structured comparison process with parallel processing"""
        task_id = str(id(websocket))
        try:
            # Process both URLs concurrently but separately
            url1_task = asyncio.create_task(
                self.process_single_url(
                    websocket,
                    urls['url1'],
                    1
                ),
                name=f"URL1-{urls['url1']}"
            )
            url2_task = asyncio.create_task(
                self.process_single_url(
                    websocket,
                    urls['url2'],
                    2
                ),
                name=f"URL2-{urls['url2']}"
            )
            self.active_tasks[task_id] = [url1_task, url2_task]

            # Wait for both URLs to be processed
            results = await asyncio.gather(url1_task, url2_task, return_exceptions=True)

            # Check for successful processing
            if any(isinstance(r, Exception) for r in results):
                error = next(r for r in results if isinstance(r, Exception))
                await self.send_status(
                    websocket,
                    "error",
                    f"Error processing URLs: {str(error)}"
                )
                return
            
            # Generate comparison
            try:
                logger.info("Generating comparison...")
                logger.info(f"Content 1 length: {len(results[0]) if results[0] else 0}")
                logger.info(f"Content 2 length: {len(results[1]) if results[1] else 0}")

                # Create a prompt for comparison
                prompt = create_prompt(
                    results[0],
                    results[1],
                    user_input['selected_categories'],
                    user_input['user_preference']
                )

                # Make call to OpenAI
                await self.send_status(websocket, "progress", f"Generating comparison...")
                try:
                    comparison = await asyncio.to_thread(call_openai_api_structured, prompt)
                    await self.send_status(websocket, "comparison", None, comparison)
                except HTTPException as e:
                    logger.error(f"Error generating comparison: {str(e)}")
                    await self.send_status(
                        websocket,
                        "error",
                        f"Error generating comparison: {str(e.detail)}"
                    )
                except Exception as e:
                    logger.error(f"Unexpected error in comparison: {str(e)}")
                    await self.send_status(
                        websocket,
                        "error",
                        f"Unexpected error: {str(e)}"
                    )
                if isinstance(comparison, ProductComparison):
                    comparison_data = comparison.dict()
                else:
                    comparison_data = None
                await self.send_status(websocket, "comparison", None, comparison_data)

            except Exception as e:
                logger.error(f"Error generating comparison: {str(e)}")
                await self.send_status(
                    websocket,
                    "error",
                    f"Error generating comparison: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Unexpected error in comparison: {str(e)}")
            await self.send_status(
                websocket,
                "error",
                f"Unexpected error: {str(e)}"
            )

        finally:
            self.active_tasks.pop(task_id, None)

    async def process_single_url(self, websocket: WebSocket, url: str, url_number: int,) -> Optional[str]:
        """Process a single URL and return its content"""
        task_id = str(id(websocket))
        logger.info(f"Processing URL {url_number}: {url}")

        try:
            if task_id in self._closed_websockets:
                return None

            # Scrape URL
            await self.send_status(websocket, "progress", f"Gathering info...")

            # Pass task_id to get_with_selenium_async
            html_content = await get_with_selenium_async(url, task_id=task_id)
            logger.info(f"[URL{url_number}] Raw HTML length: {len(html_content)}")

            # Clean HTML
            await self.send_status(websocket, "progress", f"Analyzing...")
            parsed_content = clean_html(html_content)
            logger.info(f"[URL{url_number}] Cleaned content length: {len(parsed_content)}")

            return parsed_content

        except Exception as e:
            logger.error(f"Error processing URL {url_number}: {str(e)}")
            logger.error(f"Failed URL was: {url}")
            await self.send_status(
                websocket,
                "error",
                f"Error processing URL {url_number}: {str(e)}"
            )
            return None

    async def send_status(self, websocket: WebSocket, status: str, message: Optional[str] = None, data: Optional[str] = None) -> bool:
        """Helper method to send consistent status messages to frontend"""
        try:
            msg = {
                "status": status,
                "message": message,
                "data": data
            }
            await websocket.send_json(msg)
            return True
        except Exception as e:
            logger.error(f"Error sending status: {e}")
            return False

    async def handle_client_disconnect(self, websocket: WebSocket):
        """Handle client disconnection and cleanup"""
        task_id = str(id(websocket))
        logger.info(f"Client disconnected, cleaning up task {task_id}")

        self._cancelled_tasks.add(task_id)
        self.cancel_task(task_id)
        self._closed_websockets.add(task_id)

        # Cleanup after a delay to ensure all processes are stopped
        await asyncio.sleep(1)
        self._cancelled_tasks.discard(task_id)
        self._closed_websockets.discard(task_id)
        self.active_tasks.pop(task_id, None)

    def cancel_task(self, task_id: str) -> None:
        """Cancels all tasks associated with a task_id"""
        tasks = self.active_tasks.get(task_id, [])
        for task in tasks:
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled task {task.get_name()}")

        # Clean up Selenium drivers if they're still running
        try:
            from app.services.selenium_pool import driver_pool
            driver_pool.cleanup_for_task(task_id)
        except Exception as e:
            logger.error(f"Error cleaning up Selenium drivers: {e}")
