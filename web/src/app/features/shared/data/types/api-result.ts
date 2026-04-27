export type ApiError = {
  ok: false;
  errors: string[];
  validationErrors?: Record<string, string[] | undefined>;
  data?: null;
};

export type ApiOk<T> = {
  ok: true;
  data: T;
};

export type ApiStatusOk = { ok: true };

export type ApiResult<T> = ApiOk<T> | ApiError;
export type ApiMaybeResult<T> = ApiOk<T | null> | ApiError;
export type ApiStatusResult = ApiStatusOk | ApiError;

export type ApiErrorResult = ApiError;
export type ApiSuccessResult<T> = ApiOk<T>;
export type ApiStatus = ApiStatusOk;
export type ApiLookupResult<T> = ApiMaybeResult<T>;
export type ApiNullableResult<T> = ApiMaybeResult<T>;
export type ApiActionResult = ApiStatusResult;
export type ApiStatusOrErrorResult = ApiStatusResult;
