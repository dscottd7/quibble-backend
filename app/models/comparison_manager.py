# comparison_manager.py
import asyncio
import logging
from typing import Optional, Dict, List
from fastapi import WebSocket
from app.services.get_with_selenium import get_with_selenium
from app.services.clean_html import clean_html
from app.services.openai_service import call_openai_api
from app.services.prompt_service import create_summary_prompt, create_comparison_prompt

logger = logging.getLogger(__name__)


async def generate_summary(content: str, user_input: dict) -> str:
    """Generate summary using OpenAI API"""
    prompt = create_summary_prompt(
        content, 
        user_input['selected_categories'], 
        user_input['user_preference']
    )
    return await asyncio.to_thread(call_openai_api, prompt)


async def generate_comparison(content1: str, content2: str) -> str:
    """Generate comparison using OpenAI API"""
    prompt = create_comparison_prompt(
        content1,
        content2
    )
    return await asyncio.to_thread(call_openai_api, prompt)


class ComparisonManager:
    def __init__(self):
        self.active_tasks: Dict[str, List[asyncio.Task]] = {}
        self._closed_websockets: set[str] = set() 

    async def process_single_url(
        self,
        websocket: WebSocket,
        url: str,
        url_number: int,
        user_input: dict
    ) -> Optional[str]:
        """Process a single URL's pipeline independently"""
        task_id = str(id(websocket))
        logger.info(f"Processing URL {url_number}: {url}")
        
        try:
            if task_id in self._closed_websockets:
                return None

            # Step 1: Scrape URL
            await self.send_status(websocket, "progress", f"Scraping URL {url_number}...")
            
            # Get HTML content
            html_content = await get_with_selenium(url)
            logger.info(f"[URL{url_number}] Raw HTML length: {len(html_content)}")
            
            # Clean HTML
            parsed_content = clean_html(html_content)
            logger.info(f"[URL{url_number}] Cleaned content: {parsed_content[:200]}...")  # Log first 200 chars
            
            # Step 2: Generate summary
            logger.info(f"[URL{url_number}] Generating summary")
            summary = await generate_summary(parsed_content, user_input)
            logger.info(f"[URL{url_number}] Generated summary: {summary[:200]}...")  # Log first 200 chars
            
            await self.send_status(websocket, f"summary{url_number}", None, summary)
            
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

    async def send_status(
        self,
        websocket: WebSocket,
        status: str,
        message: Optional[str] = None,
        data: Optional[str] = None
    ) -> bool:
        """Helper method to send consistent status messages"""
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

    async def start_comparison(
        self,
        websocket: WebSocket,
        urls: dict,
        user_input: dict
    ) -> None:
        """Manages the comparison process with parallel processing"""
        task_id = str(id(websocket))
        
        try:
            # Process both URLs concurrently but separately
            url1_task = asyncio.create_task(
                self.process_single_url(
                    websocket,
                    urls['url1'],
                    1,
                    user_input
                ),
                name=f"URL1-{urls['url1']}"
            )
            
            url2_task = asyncio.create_task(
                self.process_single_url(
                    websocket,
                    urls['url2'],
                    2,
                    user_input
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
                
            # Generate final comparison using the processed content
            try:
                logger.info("Generating final comparison...")
                logger.info(f"Content 1 length: {len(results[0]) if results[0] else 0}")
                logger.info(f"Content 2 length: {len(results[1]) if results[1] else 0}")
                
                comparison = await generate_comparison(results[0], results[1])
                await self.send_status(websocket, "comparison", None, comparison)
                
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

    def cancel_task(self, task_id: str) -> None:
        """Cancels all tasks associated with a task_id"""
        tasks = self.active_tasks.get(task_id, [])
        for task in tasks:
            if not task.done():
                task.cancel()
        self.active_tasks.pop(task_id, None)