import openai

class Chat:
    def __init__(self, api_key, base_url="https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant"}
        ]
        
    
    def chat(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.conversation_history,
                stream=False
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            print(f"Error: {e}")
            self.conversation_history.append({"role": "assistant", "content": " "})
            return "##API失效"
    
    def clear_history(self):
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant"}
        ]




