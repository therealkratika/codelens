ANSWER_EVALUATION_DATASET = [
    {
        "question": "How is a battle created?",
        "expected_sources": [
            "frontend/components/battle/CreateBattleForm.tsx",
            "frontend/lib/api.ts",
            "backend/src/controller/battleController.js",
        ],
    },
    {
        "question": "How does a player join a battle?",
        "expected_sources": [
            "frontend/components/lobby/JoinBattleForm.tsx",
            "frontend/lib/api.ts",
            "backend/src/controller/battleController.js",
            "backend/src/socket/handlers/joinRoom.js",
        ],
    },
    {
        "question": "How are battle questions selected?",
        "expected_sources": [
            "backend/src/controller/battleController.js",
            "backend/src/services/questionService.js",
            "backend/src/socket/handlers/startBattle.js",
        ],
    },
]