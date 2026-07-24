# Data Structure of AI Responses:
#   response    --> choices[] -->   message --> role / content / tool_calls
#   chunk       --> choices[] -->   delta   --> role / content / tool_calls
#
#   response    --> usage   --> prompt_tokens / completion_tokens / total_tokens