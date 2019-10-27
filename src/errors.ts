export enum ErrorType {
  INTERNAL = 500,
  UNAUTHORIZED = 401,
}

export class TypedError extends Error {
  constructor(public errorType: ErrorType, message: string, err?: any) {
    super(message);
    if (err && err.stack) {
      this.stack += '\n\n' + err.stack;
    }
  }
}

export function newInternalError(message: string, err?: any): TypeError {
  return new TypedError(ErrorType.INTERNAL, message, err);
}

export function newUnauthorizedError(message: string, err?: any): TypeError {
  return new TypedError(ErrorType.UNAUTHORIZED, message, err);
}
