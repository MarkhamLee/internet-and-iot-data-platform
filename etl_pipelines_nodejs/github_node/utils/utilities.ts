// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import axios from 'axios';
import {InfluxDB} from '@influxdata/influxdb-client';
import { config } from '../utils/gh_actions_config'

const buildUrl = (repo: string) => {

    const baseUrl = 'https://api.github.com/repos/MarkhamLee/'

    const endpoint = 'actions/runs'

    return baseUrl.concat(repo, endpoint)

}


export { buildUrl }