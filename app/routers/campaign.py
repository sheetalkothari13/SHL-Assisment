from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.campaign import Campaign, CampaignItem
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignItemCreate
from app.logging_config import logger
from typing import List

router = APIRouter(prefix="/campaigns", tags=["Campaign Spec Builder"])

@router.post("", response_model=CampaignResponse)
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_db)):
    """Finalize assessment selection and persist a Campaign Specification"""
    campaign = Campaign(
        title=payload.title,
        role_name=payload.role_name,
        seniority=payload.seniority,
        notes=payload.notes
    )
    campaign.target_skills = payload.target_skills
    db.add(campaign)
    await db.flush() # Flush to get generated UUID id
    
    for item in payload.items:
        campaign_item = CampaignItem(
            campaign_id=campaign.id,
            assessment_name=item.assessment_name,
            assessment_code=item.assessment_code,
            assessment_type=item.assessment_type,
            assessment_url=item.assessment_url,
            why_selected=item.why_selected
        )
        db.add(campaign_item)
        
    await db.commit()
    await db.refresh(campaign)
    
    # Return formatted schema
    return CampaignResponse(
        id=campaign.id,
        title=campaign.title,
        role_name=campaign.role_name,
        seniority=campaign.seniority,
        target_skills=campaign.target_skills,
        notes=campaign.notes,
        created_at=campaign.created_at.isoformat(),
        items=[
            CampaignItemCreate(
                assessment_name=i.assessment_name,
                assessment_code=i.assessment_code,
                assessment_type=i.assessment_type,
                assessment_url=i.assessment_url,
                why_selected=i.why_selected
            ) for i in campaign.items
        ]
    )

@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    """List all saved recruitment campaign specifications"""
    result = await db.execute(
        select(Campaign).order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    
    responses = []
    for c in campaigns:
        responses.append(
            CampaignResponse(
                id=c.id,
                title=c.title,
                role_name=c.role_name,
                seniority=c.seniority,
                target_skills=c.target_skills,
                notes=c.notes,
                created_at=c.created_at.isoformat(),
                items=[
                    CampaignItemCreate(
                        assessment_name=i.assessment_name,
                        assessment_code=i.assessment_code,
                        assessment_type=i.assessment_type,
                        assessment_url=i.assessment_url,
                        why_selected=i.why_selected
                    ) for i in c.items
                ]
            )
        )
    return responses

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single campaign configuration specification"""
    result = await db.execute(
        select(Campaign).filter(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign specification not found.")
        
    return CampaignResponse(
        id=campaign.id,
        title=campaign.title,
        role_name=campaign.role_name,
        seniority=campaign.seniority,
        target_skills=campaign.target_skills,
        notes=campaign.notes,
        created_at=campaign.created_at.isoformat(),
        items=[
            CampaignItemCreate(
                assessment_name=i.assessment_name,
                assessment_code=i.assessment_code,
                assessment_type=i.assessment_type,
                assessment_url=i.assessment_url,
                why_selected=i.why_selected
            ) for i in campaign.items
        ]
    )

@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a campaign configuration"""
    result = await db.execute(
        select(Campaign).filter(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign specification not found.")
        
    await db.delete(campaign)
    await db.commit()
    return {"status": "success", "message": f"Campaign spec {campaign_id} successfully deleted."}
