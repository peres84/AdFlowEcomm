from fastapi import APIRouter, status
from app.models.form import FormSubmission, FormSubmissionResponse
from app.services import session_manager
from app.core import SessionNotFoundError, log_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/form", tags=["form"])


@router.post("/submit", response_model=FormSubmissionResponse)
async def submit_form(form_data: FormSubmission):
    """
    Submit product information form data.
    
    This endpoint validates and stores form data in the user's session.
    All fields are validated using Pydantic models.
    
    Args:
        form_data: FormSubmission model containing all form fields
        
    Returns:
        FormSubmissionResponse with success status and message
        
    Raises:
        HTTPException: 404 if session not found, 500 if update fails
    """
    try:
        # Retrieve the session
        session = session_manager.get_session(form_data.session_id)
        
        if not session:
            raise SessionNotFoundError(form_data.session_id)
        
        # Update session with form data
        session.product_name = form_data.product_name
        session.category = form_data.category
        session.target_audience = form_data.target_audience
        session.main_benefit = form_data.main_benefit
        session.brand_colors = form_data.brand_colors
        session.brand_tone = form_data.brand_tone
        session.target_platform = form_data.target_platform
        session.website_url = form_data.website_url
        session.scene_description = form_data.scene_description
        
        # Save updated session
        success = session_manager.update_session(form_data.session_id, session)
        
        if not success:
            from app.core import ProductFlowError
            raise ProductFlowError(
                message="Failed to save form data. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="SESSION_UPDATE_FAILED"
            )
        
        logger.info(f"Form data saved successfully for session: {form_data.session_id}")
        
        return FormSubmissionResponse(
            success=True,
            message="Form data saved successfully",
            session_id=form_data.session_id
        )
        
    except (SessionNotFoundError, Exception) as e:
        log_error(
            e,
            context={"endpoint": "/api/form/submit"},
            session_id=form_data.session_id
        )
        raise
