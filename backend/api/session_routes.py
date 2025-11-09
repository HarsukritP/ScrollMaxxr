"""
Session Management API Routes
Handles Playwright-based calibration sessions
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import uuid
import json

from automation.session_manager import (
    create_session,
    get_session,
    stop_session,
    list_sessions
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session", tags=["sessions"])


class SessionStartRequest(BaseModel):
    """Request to start a new calibration session"""
    category: str
    categoryDescription: str
    cookies: List[Dict]  # TikTok cookies from user's browser
    userAgent: str


class SessionResponse(BaseModel):
    """Response with session information"""
    session_id: str
    status: str
    message: str


class SessionStatusResponse(BaseModel):
    """Response with detailed session status"""
    session_id: str
    is_running: bool
    category: str
    stats: Dict


@router.post("/start", response_model=SessionResponse)
async def start_session(request: SessionStartRequest):
    """
    Start a new Playwright-based calibration session
    
    Args:
        request: SessionStartRequest with category, cookies, etc.
    
    Returns:
        SessionResponse with session_id
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        logger.info(f"Creating session {session_id}")
        logger.info(f"Category: {request.category}")
        logger.info(f"Cookies: {len(request.cookies)} cookies")
        
        # Create session
        session = create_session(
            session_id=session_id,
            category=request.category,
            category_description=request.categoryDescription,
            cookies=request.cookies,
            user_agent=request.userAgent
        )
        
        # Start session
        await session.start()
        
        return SessionResponse(
            session_id=session_id,
            status="started",
            message="Calibration session started successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/stop/{session_id}", response_model=SessionResponse)
async def stop_session_endpoint(session_id: str):
    """
    Stop an active calibration session
    
    Args:
        session_id: ID of the session to stop
    
    Returns:
        SessionResponse with status
    """
    try:
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await stop_session(session_id)
        
        return SessionResponse(
            session_id=session_id,
            status="stopped",
            message="Session stopped successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop session: {str(e)}"
        )


@router.get("/status/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get current status of a calibration session
    
    Args:
        session_id: ID of the session
    
    Returns:
        SessionStatusResponse with detailed status
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    status = session.get_status()
    return SessionStatusResponse(**status)


@router.get("/list")
async def list_active_sessions():
    """
    List all active session IDs
    
    Returns:
        List of active session IDs
    """
    sessions = list_sessions()
    return {
        "active_sessions": sessions,
        "count": len(sessions)
    }


# WebSocket for real-time stats updates
class ConnectionManager:
    """Manages WebSocket connections for each session"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Connect a WebSocket to a session"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected to session {session_id}")
    
    def disconnect(self, session_id: str, websocket: WebSocket):
        """Disconnect a WebSocket from a session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected from session {session_id}")
    
    async def send_stats(self, session_id: str, stats: Dict):
        """Send stats update to all connected clients"""
        if session_id in self.active_connections:
            # Remove dead connections
            dead_connections = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(stats)
                except Exception as e:
                    logger.error(f"Failed to send to WebSocket: {e}")
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                self.disconnect(session_id, connection)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time stats updates
    
    Connect to this endpoint to receive live stats during calibration
    """
    await manager.connect(session_id, websocket)
    
    try:
        # Set up callback for session stats
        session = get_session(session_id)
        if session:
            # Update the session's stats callback
            async def stats_callback(stats: Dict):
                await manager.send_stats(session_id, stats)
            
            session.stats_callback = stats_callback
            
            # Send initial stats
            await manager.send_stats(session_id, session.get_status())
        
        # Keep connection alive and listen for messages
        while True:
            try:
                # Receive messages (for ping/pong or commands)
                data = await websocket.receive_text()
                
                # Handle ping
                if data == "ping":
                    await websocket.send_text("pong")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    finally:
        manager.disconnect(session_id, websocket)

