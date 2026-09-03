type ApiErrorDetail = {
  code?: string;
  detail?: string;
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }

  static fromResponse(status: number, body: unknown) {
    const detail = typeof body === 'object' && body !== null && 'detail' in body ? (body.detail as ApiErrorDetail | string) : null;
    if (typeof detail === 'object' && detail !== null) {
      return new ApiError(detail.detail ?? 'Request failed.', status, detail.code);
    }
    return new ApiError(typeof detail === 'string' ? detail : 'Request failed.', status);
  }
}
