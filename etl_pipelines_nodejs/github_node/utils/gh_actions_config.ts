// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 

export interface VarConfig {
    bucket: string;
    ghToken: string;
    measurement: string;
    org: string; 
    stock: string;
    token: string;
    url: string;
    webHookUrl: string;
    
  }

export const config: VarConfig = {
    
    bucket: process.env.DEVOPS_BUCKET as string,
    ghToken: process.env.GITHUB_TOKEN as string,
    measurement: process.env.GITHUB_DATAPLATFORM_ACTIONS_MEASUREMENT as string,
    org: process.env.INFLUX_ORG as string,
    stock: process.env.STOCK_SYMBOL as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    
  };

