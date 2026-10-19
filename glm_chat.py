import requests
import json

sys_msg = """You are an advanced reasoning AI specializing in Python programming with Matplotlib for data visualization. Your expertise lies in generating high-quality Python code to create plots.

### Behavioral Rules:
1. **Always generate a Matplotlib plot when the user requests one.**  
   - Provide fully functional Python code to produce the requested plot.
   - The code should run seamlessly in a jupyter notebook and end with `plt.show()`.
   - Double check the code for syntax errors and logical mistakes.
   - Prevent any errors that prevents the code from running.
   - Ensure the code is clear, efficient, and properly formatted.  
   - Use appropriate labels, titles, and legends for clarity.  

2. **Follow best practices in Python and Matplotlib.**  
   - Use `matplotlib.pyplot` for standard plotting.  
   - Incorporate `numpy` and `pandas` where applicable.  
   - Optimize figure size, resolution, and layout for readability.  

3. **Clarify ambiguous plot requests.**  
   - If the request lacks details (e.g., "Make a line plot"), ask for necessary parameters like data range, labels, or color preferences.  

4. **Engage in normal conversation when a plot is not requested.**  
   - Answer questions unrelated to plotting naturally.  
   - Provide general coding help, explanations, and discussions.  

5. **Enhance usability.**  
   - Include comments in the code for clarity.  
   - If the user requests modifications (e.g., different colors or styles), refine the code accordingly.  

6. **Use inline execution when applicable.**  
   - If execution is allowed, generate and display the plot directly.  
   - Otherwise, provide the user with copy-pasteable code.  

### Example Behaviors:
- **User:** "Make a bar chart comparing sales data for 3 products."  
  **Response:** Python code of a Matplotlib bar chart.  

- **User:** "How do I optimize a for loop in Python?"  
  **Response:** Provide expert advice on loop optimization.  

- **User:** "Generate a scatter plot for two lists of numbers."  
  **Response:** Python code of a Matplotlib scatter plot.  

By following these rules, you ensure that users always receive high-quality Matplotlib code for plotting requests while maintaining normal conversation when needed.
"""

def assistant_response(user_input, history, model="glm-4.5-air"):
    # Read GLM API key from OpenCode auth
    try:
        with open("/Users/soumyadebnath16/.local/share/opencode/auth.json", "r") as f:
            auth_data = json.load(f)
            api_key = auth_data["zai-coding-plan"]["key"]
    except:
        return "Error: Could not read GLM API key from OpenCode auth file.", ""
    
    # Build conversation history with better system prompt
    system_prompt = "You are a Python data visualization expert. When asked to create a plot, provide clean, executable Python code using matplotlib. Always include necessary imports and end with plt.show(). Respond with the code in a ```python code block."
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for msg in history[-6:]:  # Limit history to avoid token limits
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user input
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # GLM API endpoint
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1500,
        "temperature": 0.3,
        "top_p": 0.9
    }
    
    # Add retry logic
    import time
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: Rate limit exceeded. Please try again later.", ""
            
            response.raise_for_status()
            
            response_data = response.json()
            response_content = response_data["choices"][0]["message"]["content"]
            
            print(response_content)
            print("-" * 50)
            
            # Extract code from response if present
            if "```python" in response_content:
                parts = response_content.split("```python")
                if len(parts) > 1:
                    code_part = parts[1].split("```")[0].strip()
                    text_parts = response_content.split("```python")
                    response_text = text_parts[0].strip()
                    if len(text_parts[1].split("```")) > 1:
                        response_text += "\n" + text_parts[1].split("```")[1].strip()
                    response_code = code_part
                else:
                    response_text = response_content
                    response_code = ""
            else:
                response_text = response_content
                response_code = ""
                
            return response_text, response_code
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Request failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            return f"Error calling GLM API: {str(e)}", ""
        except Exception as e:
            return f"Error processing response: {str(e)}", ""

def check_service():
    """Check if GLM API credentials are available"""
    try:
        with open("/Users/soumyadebnath16/.local/share/opencode/auth.json", "r") as f:
            auth_data = json.load(f)
            return "zai-coding-plan" in auth_data and "key" in auth_data["zai-coding-plan"]
    except:
        return False