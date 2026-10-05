import re


class APIFlowAnalyzer:

    HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    def extract_base_endpoints(self, code):

        endpoints = {}

        base_url_match = re.search(
            r'API_BASE_URL\s*=\s*["\']([^"\']+)["\']',
            code
        )

        base_url = (
            base_url_match.group(1)
            if base_url_match
            else None
        )

        if not base_url:
            return endpoints

        endpoint_pattern = re.compile(
            r'(API_ENDPOINT|SUBMISSION_ENDPOINT)'
            r'\s*=\s*`\$\{API_BASE_URL\}([^`]*)`'
        )

        for match in endpoint_pattern.finditer(code):
            name = match.group(1)
            path = match.group(2)
            endpoints[name] = base_url + path

        return endpoints

    def analyze(self, file_path, code):
        results = []

        if not file_path.endswith(("api.js", "api.ts", "api.jsx", "api.tsx")):
            return results

        # ---------------------------------------------------------
        # 1. Extract base URL
        # ---------------------------------------------------------

        base_url_match = re.search(
            r'API_BASE_URL\s*=\s*["\']([^"\']+)["\']',
            code
        )

        base_url = base_url_match.group(1) if base_url_match else None

        # ---------------------------------------------------------
        # 2. Extract endpoint constants
        # ---------------------------------------------------------

        endpoints = {}

        endpoint_pattern = re.compile(
            r'(API_ENDPOINT|SUBMISSION_ENDPOINT)'
            r'\s*=\s*`\$\{API_BASE_URL\}([^`]*)`'
        )

        for match in endpoint_pattern.finditer(code):
            name = match.group(1)
            path = match.group(2)

            if base_url:
                endpoints[name] = base_url + path
            else:
                endpoints[name] = path

        # ---------------------------------------------------------
        # 3. Find API functions
        # ---------------------------------------------------------

        function_pattern = re.compile(
            r"(?:export\s+)?"
            r"(?:default\s+)?"
            r"(?:async\s+)?"
            r"function\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*\(",
            re.MULTILINE,
        )

        functions = list(function_pattern.finditer(code))

        for index, function_match in enumerate(functions):

            function_name = function_match.group(1)

            start = function_match.start()

            end = (
                functions[index + 1].start()
                if index + 1 < len(functions)
                else len(code)
            )

            function_code = code[start:end]

            # -----------------------------------------------------
            # 4. Find apiRequest(...)
            # -----------------------------------------------------

            request_pattern = re.compile(
                r"apiRequest"
                r"(?:<[\s\S]*?>)?"
                r"\s*\("
                r"\s*"
                r"([\"'`])"
                r"([^\"'`]+)"
                r"\1",
                re.MULTILINE,
            )

            request_match = request_pattern.search(function_code)

            if not request_match:
                continue

            endpoint = request_match.group(2)

            # -----------------------------------------------------
            # 5. HTTP method
            # -----------------------------------------------------

            method_match = re.search(
                r"method\s*:\s*[\"']"
                r"(GET|POST|PUT|PATCH|DELETE)"
                r"[\"']",
                function_code,
                re.IGNORECASE,
            )

            method = (
                method_match.group(1).upper()
                if method_match
                else "GET"
            )

            # -----------------------------------------------------
            # 6. Detect endpoint variable
            # -----------------------------------------------------

            endpoint_variable = None

            request_start = request_match.start()

            request_code = function_code[request_start:]

            variable_match = re.search(
                r",\s*\{[\s\S]*?\}\s*,\s*"
                r"([A-Z][A-Z0-9_]*)\s*\)",
                request_code,
                re.MULTILINE,
            )

            if variable_match:
                endpoint_variable = variable_match.group(1)

            # -----------------------------------------------------
            # 7. Resolve full endpoint
            # -----------------------------------------------------

            resolved_endpoint = endpoint

            base_endpoint_name = (
                endpoint_variable
                if endpoint_variable is not None
                else "API_ENDPOINT"
            )

            if base_endpoint_name in endpoints:
                resolved_endpoint = (
                    endpoints[base_endpoint_name] + endpoint
                )

            # -----------------------------------------------------
            # 8. Line number
            # -----------------------------------------------------

            line_number = code[:start].count("\n") + 1

            # -----------------------------------------------------
            # 9. Store result
            # -----------------------------------------------------

            results.append({
                "function": function_name,
                "method": method,
                "endpoint": endpoint,
                "resolved_endpoint": resolved_endpoint,
                "endpoint_variable": endpoint_variable,
                "line": line_number,
                "file": file_path,
            })

        return results