/**
 * async-handler.ts — wraps an async Express handler so that a rejected promise
 * is forwarded to Express's error-handling middleware via next(err) instead of
 * becoming an unhandled rejection that can crash the process.
 */
import type { Request, Response, NextFunction, RequestHandler } from "express";

type AsyncRequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction,
) => Promise<unknown> | unknown;

export function asyncHandler(fn: AsyncRequestHandler): RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

/**
 * Strip CR/LF and quote characters from a value before it is interpolated into
 * an HTTP response header (e.g. a Content-Disposition filename), preventing
 * header injection / response splitting.
 */
export function sanitizeHeaderValue(value: string): string {
  return value.replace(/[\r\n"\\]/g, "_").trim();
}
