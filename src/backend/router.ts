import fs = require('fs');
import http = require('http');
import https = require('https');
import url = require('url');
import { CONTENT_TYPE_TEXT, HttpMethod } from './common';
import { TypedError, newInternalError, ErrorType } from '../errors';
import { HttpHandler, HttpResponse } from './http_handler';
import { LOGGER } from './logger';

interface HttpsOption {
  key: string,
  cert: string,
  ca: string[],
}

// TODO: Rate limit requests.
export class Router {
  private static HTTP_PORT = 80;
  private static HTTPS_PORT = 443;
  private static CONTENT_TYPE_HEADER = 'Content-Type';
  private static ALLOW_ORIGIN_HEADER = 'Access-Control-Allow-Origin';
  private static ALLOW_METHODS_HEADER = 'Access-Control-Allow-Methods';
  private static ALLOW_HEADERS_HEADER = 'Access-Control-Allow-Headers';
  private static LOCATION_HEADER = 'Location';
  private static REDIRECT_CODE = 301;
  private static OK_CODE = 200;
  private static REQUEST_ID_RANDOM_MAX = 10000;
  private static HTTPS_PROTOCAL = 'https://';

  private handlers: HttpHandler[] = [];

  public constructor(private hostname: string, private httpServer: http.Server, private httpsServer?: https.Server) {}

  public init(): void {
    if (this.httpsServer) {
      this.httpServer.addListener('request',
        (request: http.IncomingMessage, response: http.ServerResponse): void => this.redirectToHttps(request, response));
      this.httpsServer.addListener('request',
        (request: http.IncomingMessage, response: http.ServerResponse): Promise<void> => this.handle(request, response));
    } else {
      this.httpServer.addListener('request',
        (request: http.IncomingMessage, response: http.ServerResponse): Promise<void> => this.handle(request, response));
    }
  }

  private redirectToHttps(request: http.IncomingMessage, response: http.ServerResponse): void {
    LOGGER.info(`Redirecting to ${Router.HTTPS_PROTOCAL + this.hostname + request.url}.`);
    response.setHeader(Router.ALLOW_ORIGIN_HEADER, '*');
    response.setHeader(Router.ALLOW_METHODS_HEADER, '*');
    response.setHeader(Router.ALLOW_HEADERS_HEADER, '*');
    response.writeHead(Router.REDIRECT_CODE, {[Router.LOCATION_HEADER]: this.hostname + request.url});
    response.end();
  }

  private async handle(request: http.IncomingMessage, response: http.ServerResponse): Promise<void> {
    let randomId = Math.floor(Math.random() * Router.REQUEST_ID_RANDOM_MAX);
    let logContext = `Request ${Date.now()}-${randomId}: `;

    response.setHeader(Router.ALLOW_ORIGIN_HEADER, '*');
    response.setHeader(Router.ALLOW_METHODS_HEADER, '*');
    response.setHeader(Router.ALLOW_HEADERS_HEADER, '*');

    let httpResponse: HttpResponse;
    try {
      httpResponse = await this.dispatch(logContext, request);
    } catch (error) {
      LOGGER.error(logContext + error.stack);
      if (error.errorType) {
        response.writeHead((error as TypedError).errorType, {[Router.CONTENT_TYPE_HEADER]: CONTENT_TYPE_TEXT});
      } else {
        response.writeHead(ErrorType.INTERNAL, {[Router.CONTENT_TYPE_HEADER]: CONTENT_TYPE_TEXT});
      }
      response.end(error.message);
      return;
    }

    response.writeHead(Router.OK_CODE, {[Router.CONTENT_TYPE_HEADER]: httpResponse.contentType});
    if (!httpResponse.contentFile) {
      response.end(httpResponse.content);
    } else {
      let readStream = fs.createReadStream(httpResponse.contentFile);
      readStream.on('error', (err: Error): void => {
        LOGGER.error(logContext + err.stack);
        response.end();
      });
      readStream.on('close', (): void => {
        LOGGER.info(logContext + `File, ${httpResponse.contentFile}, was closed.`);
        response.end();
      });
      response.on('error', (err): void => {
        LOGGER.error(logContext + err.stack);
        readStream.close();
      });
      response.on('close', (): void => {
        LOGGER.info(logContext + 'Response closed.');
        readStream.close();
      });
      readStream.pipe(response);
    }
  }

  private async dispatch(logContext: string, request: http.IncomingMessage): Promise<HttpResponse> {
    let method = request.method.toUpperCase();
    let parsedUrl = url.parse(request.url);

    LOGGER.info(logContext
      + `Request received:\n`
      + `pathname: ${parsedUrl.pathname}\n`
      + `method: ${method}`);

    for (let i = 0; i < this.handlers.length; i++) {
      let handler = this.handlers[i];
      if (method === HttpMethod[handler.method] && parsedUrl.pathname.match(handler.urlRegex)) {
        LOGGER.info(logContext + `Handler ${i} matched request with [${handler.urlRegex}, ${handler.method}].`)
        return handler.handle(logContext, request, parsedUrl);
      }
    }

    throw newInternalError(`404 Not Found :/`);
  }

  public start(): void {
    this.httpServer.listen(Router.HTTP_PORT);
    LOGGER.info(`Http server started at ${Router.HTTP_PORT}.`);
    this.httpsServer.listen(Router.HTTPS_PORT);
    LOGGER.info(`Https server started at ${Router.HTTPS_PORT}.`);
  }

  public addHandler(httpHandler: HttpHandler): void {
    this.handlers.push(httpHandler);
  }
}

export class RouterFactory {
  public get(hostname: string, httpsOption?: HttpsOption): Router {
    let httpServer = http.createServer();
    let httpsServer = undefined;
    if (httpsOption) {
      httpsServer = https.createServer(httpsOption);
    }
    let router = new Router(hostname, httpServer, httpsServer);
    router.init();
    return router;
  }
}

export let ROUTER_FACTORY = new RouterFactory();
