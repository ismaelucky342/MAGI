import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export interface ErrorWithStatus extends Error {
  status?: number;
  statusCode?: number;
}

export const errorHandler = (
  err: ErrorWithStatus,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  logger.error('Error:', {
    status,
    message,
    stack: err.stack,
    url: req.url,
    method: req.method,
  });

  res.status(status).json({
    error: {
      status,
      message: process.env.NODE_ENV === 'production' ? 'Internal Server Error' : message,
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
    },
  });
};

export const notFound = (req: Request, res: Response, next: NextFunction) => {
  const err = new Error(`Not Found - ${req.originalUrl}`) as ErrorWithStatus;
  err.status = 404;
  next(err);
};
