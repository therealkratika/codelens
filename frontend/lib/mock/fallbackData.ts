import type { FeatureFlow, CodeGraphData } from "@/types/architecture";
import type { FileNode, FileContentResponse } from "@/types/files";

export const FALLBACK_FLOWS: FeatureFlow[] = [
  {
    id: "frontend/lib/api.ts:createBattle",
    name: "createBattle",
    description: "Generates a unique room code and initializes a new coding battle match.",
    frontend_api: {
      function: "createBattle",
      method: "POST",
      endpoint: "/create",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/create",
      file: "frontend/lib/api.ts",
      line: 176,
    },
    route: {
      method: "POST",
      path: "/api/battle/create",
      handler: "createBattle",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 11,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "createBattle",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "createBattle",
      controller_start_line: 8,
      controller_end_line: 55,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
      {
        symbol: "generateUniqueRoomCode",
        target_file: "backend/src/utils/generateRoomCode.js",
        import_source: "../utils/generateRoomCode.js",
        type: "named",
      },
    ],
  },
  {
    id: "frontend/lib/api.ts:joinBattle",
    name: "joinBattle",
    description: "Validates room code, registers opponent player, and transitions battle status.",
    frontend_api: {
      function: "joinBattle",
      method: "POST",
      endpoint: "/join",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/join",
      file: "frontend/lib/api.ts",
      line: 209,
    },
    route: {
      method: "POST",
      path: "/api/battle/join",
      handler: "joinBattle",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 12,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "joinBattle",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "joinBattle",
      controller_start_line: 56,
      controller_end_line: 117,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
    ],
  },
  {
    id: "frontend/lib/api.ts:getBattle",
    name: "getBattle",
    description: "Fetches battle room details, player rosters, status, and scores.",
    frontend_api: {
      function: "getBattle",
      method: "GET",
      endpoint: "/${roomCode}",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/${roomCode.toUpperCase()}",
      file: "frontend/lib/api.ts",
      line: 233,
    },
    route: {
      method: "GET",
      path: "/api/battle/:roomCode",
      handler: "getBattle",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 16,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "getBattle",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "getBattle",
      controller_start_line: 118,
      controller_end_line: 143,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
    ],
  },
  {
    id: "frontend/lib/api.ts:getBattleQuestions",
    name: "getBattleQuestions",
    description: "Retrieves curated coding battle problems, test cases, and constraints.",
    frontend_api: {
      function: "getBattleQuestions",
      method: "GET",
      endpoint: "/${roomCode}/questions",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/${roomCode.toUpperCase()}/questions",
      file: "frontend/lib/api.ts",
      line: 267,
    },
    route: {
      method: "GET",
      path: "/api/battle/:roomCode/questions",
      handler: "getBattleQuestions",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 13,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "getBattleQuestions",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "getBattleQuestions",
      controller_start_line: 144,
      controller_end_line: 181,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
      {
        symbol: "Question",
        target_file: "backend/src/model/question.js",
        import_source: "../model/question.js",
        type: "default",
      },
      {
        symbol: "sanitizeQuestion",
        target_file: "backend/src/services/questionService.js",
        import_source: "../services/questionService.js",
        type: "named",
      },
    ],
  },
  {
    id: "frontend/lib/api.ts:getBattleSubmissions",
    name: "getBattleSubmissions",
    description: "Fetches code submissions, evaluation statuses, and execution runtime logs.",
    frontend_api: {
      function: "getBattleSubmissions",
      method: "GET",
      endpoint: "/${roomCode}/submissions",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/${roomCode.toUpperCase()}/submissions",
      file: "frontend/lib/api.ts",
      line: 300,
    },
    route: {
      method: "GET",
      path: "/api/battle/:roomCode/submissions",
      handler: "getBattleSubmissions",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 14,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "getBattleSubmissions",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "getBattleSubmissions",
      controller_start_line: 182,
      controller_end_line: 266,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
      {
        symbol: "Submission",
        target_file: "backend/src/model/submission.js",
        import_source: "../model/submission.js",
        type: "default",
      },
    ],
  },
  {
    id: "frontend/lib/api.ts:leaveBattle",
    name: "leaveBattle",
    description: "Safely exits room and notifies participants via socket disconnection.",
    frontend_api: {
      function: "leaveBattle",
      method: "POST",
      endpoint: "/leave",
      resolved_endpoint: "https://nextja-coding-battle.onrender.com/api/battle/leave",
      file: "frontend/lib/api.ts",
      line: 254,
    },
    route: {
      method: "POST",
      path: "/api/battle/leave",
      handler: "leaveBattle",
      route_file: "backend/src/routes/battleRoutes.js",
      route_line: 17,
      mount_file: "backend/server.js",
      mount_line: 27,
    },
    controller: {
      handler: "leaveBattle",
      controller_file: "backend/src/controller/battleController.js",
      controller_function: "leaveBattle",
      controller_start_line: 267,
      controller_end_line: 314,
    },
    dependencies: [
      {
        symbol: "Battle",
        target_file: "backend/src/model/battle.js",
        import_source: "../model/battle.js",
        type: "default",
      },
    ],
  },
];

export const FALLBACK_GRAPH: CodeGraphData = {
  summary: {
    nodes: 56,
    edges: 11,
  },
  nodes: [
    {
      id: "frontend/lib/api.ts",
      file: "frontend/lib/api.ts",
      imports: [{ source: "axios", names: ["axios"] }],
      functions: [
        { name: "createBattle", start_line: 176, end_line: 207 },
        { name: "joinBattle", start_line: 209, end_line: 231 },
        { name: "getBattle", start_line: 233, end_line: 252 },
        { name: "leaveBattle", start_line: 254, end_line: 265 },
        { name: "getBattleQuestions", start_line: 267, end_line: 298 },
        { name: "getBattleSubmissions", start_line: 300, end_line: 330 },
      ],
      calls: [{ name: "axios.post", start_line: 180 }],
      imports_count: 1,
      functions_count: 6,
      calls_count: 6,
    },
    {
      id: "backend/server.js",
      file: "backend/server.js",
      imports: [
        { source: "express", names: ["express"] },
        { source: "./src/routes/battleRoutes", names: ["battleRoutes"] },
      ],
      functions: [],
      calls: [{ name: "app.use", start_line: 27 }],
      imports_count: 2,
      functions_count: 0,
      calls_count: 5,
    },
    {
      id: "backend/src/routes/battleRoutes.js",
      file: "backend/src/routes/battleRoutes.js",
      imports: [
        { source: "express", names: ["Router"] },
        {
          source: "../controller/battleController",
          names: ["createBattle", "joinBattle", "getBattle", "getBattleQuestions"],
        },
      ],
      functions: [],
      calls: [{ name: "router.post", start_line: 11 }],
      imports_count: 2,
      functions_count: 0,
      calls_count: 6,
    },
    {
      id: "backend/src/controller/battleController.js",
      file: "backend/src/controller/battleController.js",
      imports: [
        { source: "../model/battle", names: ["Battle"] },
        { source: "../model/question", names: ["Question"] },
      ],
      functions: [
        { name: "createBattle", start_line: 8, end_line: 55 },
        { name: "joinBattle", start_line: 56, end_line: 117 },
        { name: "getBattle", start_line: 118, end_line: 143 },
        { name: "getBattleQuestions", start_line: 144, end_line: 181 },
        { name: "getBattleSubmissions", start_line: 182, end_line: 266 },
        { name: "leaveBattle", start_line: 267, end_line: 314 },
      ],
      calls: [{ name: "Battle.create", start_line: 22 }],
      imports_count: 2,
      functions_count: 6,
      calls_count: 14,
    },
    {
      id: "backend/src/model/battle.js",
      file: "backend/src/model/battle.js",
      imports: [{ source: "mongoose", names: ["mongoose"] }],
      functions: [],
      calls: [],
      imports_count: 1,
      functions_count: 0,
      calls_count: 2,
    },
  ],
  edges: [
    {
      source: "backend/server.js",
      target: "backend/src/routes/battleRoutes.js",
      relation: "imports",
    },
    {
      source: "backend/src/routes/battleRoutes.js",
      target: "backend/src/controller/battleController.js",
      relation: "imports",
    },
    {
      source: "backend/src/controller/battleController.js",
      target: "backend/src/model/battle.js",
      relation: "imports",
    },
    {
      source: "backend/src/controller/battleController.js",
      target: "backend/src/model/question.js",
      relation: "imports",
    },
    {
      source: "frontend/app/layout.tsx",
      target: "frontend/app/globals.css",
      relation: "imports",
    },
  ],
};

export const FALLBACK_FILE_TREE: FileNode[] = [
  {
    name: "backend",
    path: "backend",
    type: "directory",
    children: [
      {
        name: "server.js",
        path: "backend/server.js",
        type: "file",
        size: 1420,
        extension: ".js",
        chunk_count: 3,
      },
      {
        name: "package.json",
        path: "backend/package.json",
        type: "file",
        size: 890,
        extension: ".json",
        chunk_count: 1,
      },
      {
        name: "src",
        path: "backend/src",
        type: "directory",
        children: [
          {
            name: "routes",
            path: "backend/src/routes",
            type: "directory",
            children: [
              {
                name: "battleRoutes.js",
                path: "backend/src/routes/battleRoutes.js",
                type: "file",
                size: 980,
                extension: ".js",
                chunk_count: 2,
              },
            ],
          },
          {
            name: "controller",
            path: "backend/src/controller",
            type: "directory",
            children: [
              {
                name: "battleController.js",
                path: "backend/src/controller/battleController.js",
                type: "file",
                size: 8400,
                extension: ".js",
                chunk_count: 8,
              },
            ],
          },
          {
            name: "model",
            path: "backend/src/model",
            type: "directory",
            children: [
              {
                name: "battle.js",
                path: "backend/src/model/battle.js",
                type: "file",
                size: 1980,
                extension: ".js",
                chunk_count: 2,
              },
              {
                name: "question.js",
                path: "backend/src/model/question.js",
                type: "file",
                size: 1420,
                extension: ".js",
                chunk_count: 2,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    name: "frontend",
    path: "frontend",
    type: "directory",
    children: [
      {
        name: "lib",
        path: "frontend/lib",
        type: "directory",
        children: [
          {
            name: "api.ts",
            path: "frontend/lib/api.ts",
            type: "file",
            size: 11200,
            extension: ".ts",
            chunk_count: 17,
          },
        ],
      },
      {
        name: "package.json",
        path: "frontend/package.json",
        type: "file",
        size: 950,
        extension: ".json",
        chunk_count: 1,
      },
    ],
  },
  {
    name: "README.md",
    path: "README.md",
    type: "file",
    size: 3200,
    extension: ".md",
    chunk_count: 5,
  },
];

export const FALLBACK_FILE_CONTENT: Record<string, FileContentResponse> = {
  "frontend/lib/api.ts": {
    repository: "Nextja_coding_battle",
    path: "frontend/lib/api.ts",
    name: "api.ts",
    content: `import axios from "axios";

const API_BASE_URL = "https://nextja-coding-battle.onrender.com/api";

export async function createBattle(hostName: string) {
  const response = await axios.post(\`\${API_BASE_URL}/battle/create\`, {
    hostName,
  });
  return response.data;
}

export async function joinBattle(roomCode: string, playerName: string) {
  const response = await axios.post(\`\${API_BASE_URL}/battle/join\`, {
    roomCode: roomCode.toUpperCase(),
    playerName,
  });
  return response.data;
}

export async function getBattle(roomCode: string) {
  const response = await axios.get(
    \`\${API_BASE_URL}/battle/\${roomCode.toUpperCase()}\`
  );
  return response.data;
}

export async function leaveBattle(roomCode: string, playerId: string) {
  const response = await axios.post(\`\${API_BASE_URL}/battle/leave\`, {
    roomCode: roomCode.toUpperCase(),
    playerId,
  });
  return response.data;
}

export async function getBattleQuestions(roomCode: string) {
  const response = await axios.get(
    \`\${API_BASE_URL}/battle/\${roomCode.toUpperCase()}/questions\`
  );
  return response.data;
}

export async function getBattleSubmissions(roomCode: string) {
  const response = await axios.get(
    \`\${API_BASE_URL}/battle/\${roomCode.toUpperCase()}/submissions\`
  );
  return response.data;
}`,
    line_count: 50,
    size: 1420,
    chunks: [
      { start_line: 1, end_line: 25 },
      { start_line: 26, end_line: 50 },
    ],
  },
  "backend/src/routes/battleRoutes.js": {
    repository: "Nextja_coding_battle",
    path: "backend/src/routes/battleRoutes.js",
    name: "battleRoutes.js",
    content: `const express = require("express");
const router = express.Router();
const {
  createBattle,
  joinBattle,
  getBattle,
  getBattleQuestions,
  getBattleSubmissions,
  leaveBattle,
} = require("../controller/battleController");

router.post("/create", createBattle);
router.post("/join", joinBattle);
router.get("/:roomCode/questions", getBattleQuestions);
router.get("/:roomCode/submissions", getBattleSubmissions);
router.get("/:roomCode", getBattle);
router.post("/leave", leaveBattle);

module.exports = router;`,
    line_count: 20,
    size: 580,
    chunks: [{ start_line: 1, end_line: 20 }],
  },
};
