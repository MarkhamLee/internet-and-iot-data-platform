"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
exports.config = {
    bucket: process.env.BUCKET,
    ghToken: process.env.GITHUB_TOKEN,
    measurement: process.env.GITHUB_DATAPLATFORM_ACTIONS_MEASUREMENT,
    org: process.env.INFLUX_ORG,
    stock: process.env.STOCK_SYMBOL,
    token: process.env.INFLUX_KEY,
    url: process.env.INFLUX_URL,
    webHookUrl: process.env.ALERT_WEBHOOK,
};
