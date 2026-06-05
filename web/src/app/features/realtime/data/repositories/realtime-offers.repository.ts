import { Injectable, inject } from '@angular/core';

import type { ApiResult } from '../../../shared/data/types/api-result';
import type {
  OwnerAssignmentItem,
  OwnerOfferDetail,
  OwnerOfferActionResult,
  OwnerOfferHistoryItem,
  OwnerPendingOffer,
} from '../../domain/entities/owner-offer';
import { RealtimeOffersApiService } from '../api/realtime-offers-api.service';
import type {
  OwnerHistoryOfferData,
  OwnerAssignmentData,
  OwnerOfferDetailData,
  OwnerPendingOfferData,
} from '../schemas/realtime-offer.schema';

@Injectable({ providedIn: 'root' })
export class RealtimeOffersRepository {
  private readonly realtimeOffersApi = inject(RealtimeOffersApiService);

  async listMyPendingOffers(): Promise<ApiResult<OwnerPendingOffer[]>> {
    const response = await this.realtimeOffersApi.listMyPendingOffers();
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: response.data.map((offer) => this.mapPendingOffer(offer)),
    };
  }

  async getOfferDetail(assignmentId: string): Promise<ApiResult<OwnerOfferDetail>> {
    const response = await this.realtimeOffersApi.getOfferDetail(assignmentId);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapOfferDetail(response.data),
    };
  }

  async listMyOfferHistory(): Promise<ApiResult<OwnerOfferHistoryItem[]>> {
    const response = await this.realtimeOffersApi.listMyOfferHistory();
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: response.data.map((offer) => this.mapHistoryOffer(offer)),
    };
  }

  async listMyAssignments(): Promise<ApiResult<OwnerAssignmentItem[]>> {
    const response = await this.realtimeOffersApi.listMyAssignments();
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: response.data.map((assignment) => this.mapAssignment(assignment)),
    };
  }

  async downloadServiceReportPdf(assignmentId: string): Promise<ApiResult<Blob>> {
    return this.realtimeOffersApi.downloadServiceReportPdf(assignmentId);
  }

  async submitOffer(
    assignmentId: string,
    mechanicId: string,
    quotedPrice: number,
  ): Promise<ApiResult<OwnerOfferActionResult>> {
    const response = await this.realtimeOffersApi.submitOffer(assignmentId, mechanicId, quotedPrice);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapOfferAction(response.data),
    };
  }

  async rejectOffer(assignmentId: string): Promise<ApiResult<OwnerOfferActionResult>> {
    const response = await this.realtimeOffersApi.rejectOffer(assignmentId);
    if (!response.ok) {
      return response;
    }

    return {
      ok: true,
      data: this.mapOfferAction(response.data),
    };
  }

  mapOfferDetailFromSocket(payload: OwnerOfferDetailData): OwnerOfferDetail {
    return this.mapOfferDetail(payload);
  }

  private mapPendingOffer(offer: OwnerPendingOfferData): OwnerPendingOffer {
    return {
      assignmentId: offer.assignment_id,
      incidentId: offer.incident_id,
      problemId: offer.problem_id ?? null,
      problemName: offer.problem_name ?? null,
      incidentDescription: offer.incident_description ?? null,
      distanceKm: offer.distance_km ?? null,
      deliveryPrice: offer.delivery_price ?? null,
      quotedPrice: offer.quoted_price ?? null,
      notifiedAt: offer.notified_at ?? null,
      expiresAt: offer.expires_at ?? null,
    };
  }

  private mapOfferDetail(offer: OwnerOfferDetailData): OwnerOfferDetail {
    return {
      ...this.mapPendingOffer(offer),
      assignmentStatus: offer.assignment_status ?? 'pending',
      incidentStatus: offer.incident_status ?? null,
      incidentLatitude: offer.incident_latitude,
      incidentLongitude: offer.incident_longitude,
      repairShopLatitude: offer.repair_shop_latitude ?? null,
      repairShopLongitude: offer.repair_shop_longitude ?? null,
      mechanicName: offer.mechanic_name ?? null,
      evidenceUrls: offer.evidence_urls ?? [],
    };
  }

  private mapHistoryOffer(offer: OwnerHistoryOfferData): OwnerOfferHistoryItem {
    return {
      ...this.mapPendingOffer(offer),
      status: offer.status,
      respondedAt: offer.responded_at ?? null,
    };
  }

  private mapOfferAction(action: {
    assignment_id: string;
    incident_id: string;
    status: string;
    detail: string;
    next_notified_assignment_id?: string | null;
  }): OwnerOfferActionResult {
    return {
      assignmentId: action.assignment_id,
      incidentId: action.incident_id,
      status: action.status,
      detail: action.detail,
      nextNotifiedAssignmentId: action.next_notified_assignment_id ?? null,
    };
  }

  private mapAssignment(assignment: OwnerAssignmentData): OwnerAssignmentItem {
    return {
      assignmentId: assignment.assignment_id,
      incidentId: assignment.incident_id,
      problemId: assignment.problem_id ?? null,
      problemName: assignment.problem_name ?? null,
      incidentDescription: assignment.incident_description ?? null,
      distanceKm: assignment.distance_km ?? null,
      deliveryPrice: assignment.delivery_price ?? null,
      quotedPrice: assignment.quoted_price ?? null,
      status: assignment.status,
      mechanicName: assignment.mechanic_name ?? null,
      createdAt: assignment.created_at,
    };
  }
}
