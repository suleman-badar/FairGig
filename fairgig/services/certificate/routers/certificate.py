from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pydantic import BaseModel

from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
router = APIRouter(tags=['certificate'])
templates = Jinja2Templates(directory='templates')


class CertificateRequest(BaseModel):
    worker_id: str
    from_date: date
    to_date: date


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail='Invalid token') from exc


async def _fetch_verified_shifts(worker_id: str, from_date: date, to_date: date, token: str):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{settings.earnings_url}/shifts",
            params={
                'worker_id': worker_id,
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat(),
                'verification_status': 'verified',
                'per_page': 500,
                'page': 1,
            },
            headers={'Authorization': f'Bearer {token}'},
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail='Unable to fetch shifts from earnings service')
        return response.json().get('items', [])


@router.post('/certificate')
async def generate_certificate(payload: CertificateRequest, request: Request, token: str = Depends(oauth2_scheme)):
    claims = _decode_token(token)
    if claims.get('sub') != payload.worker_id and claims.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Worker mismatch for certificate request')

    shifts = await _fetch_verified_shifts(payload.worker_id, payload.from_date, payload.to_date, token)

    by_platform = defaultdict(lambda: {'shifts': 0, 'hours': 0.0, 'gross': 0.0, 'deductions': 0.0, 'net': 0.0})
    total = {'shifts': 0, 'hours': 0.0, 'gross': 0.0, 'deductions': 0.0, 'net': 0.0}

    for s in shifts:
        p = s.get('platform', 'Other')
        by_platform[p]['shifts'] += 1
        by_platform[p]['hours'] += float(s.get('hours_worked', 0) or 0)
        by_platform[p]['gross'] += float(s.get('gross_earned', 0) or 0)
        by_platform[p]['deductions'] += float(s.get('platform_deductions', 0) or 0)
        by_platform[p]['net'] += float(s.get('net_received', 0) or 0)

        total['shifts'] += 1
        total['hours'] += float(s.get('hours_worked', 0) or 0)
        total['gross'] += float(s.get('gross_earned', 0) or 0)
        total['deductions'] += float(s.get('platform_deductions', 0) or 0)
        total['net'] += float(s.get('net_received', 0) or 0)

    context = {
        'request': request,
        'generated_at': datetime.now(UTC),
        'certificate_id': str(uuid4()),
        'worker': {
            'id': payload.worker_id,
            'full_name': 'Worker',
            'phone': 'N/A',
            'category': 'N/A',
            'city_zone': 'N/A',
        },
        'from_date': payload.from_date,
        'to_date': payload.to_date,
        'platform_rows': by_platform,
        'total': total,
        'verified_count': total['shifts'],
        'total_count': total['shifts'],
    }

    return templates.TemplateResponse('income_certificate.html', context)


@router.get('/certificate/preview/{worker_id}')
async def preview(worker_id: str, request: Request, token: str = Depends(oauth2_scheme)):
    today = date.today()
    payload = CertificateRequest(worker_id=worker_id, from_date=today - timedelta(days=30), to_date=today)
    return await generate_certificate(payload, request, token)
