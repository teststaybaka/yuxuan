import http = require('http');
import url = require('url');
import { HttpMethod } from './common';

export class HttpResponse {
  contentType: string;
  // One of the below.
  content?: string;
  contentFile?: string;
}

export interface HttpHandler {
  method: HttpMethod,
  urlRegex: RegExp,
  handle: ((logContext: string, request: http.IncomingMessage, parsedUrl: url.Url) => Promise<HttpResponse>),
}
