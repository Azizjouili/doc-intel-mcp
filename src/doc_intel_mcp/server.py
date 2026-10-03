from mcp.server.mcpserver import MCPServer

from doc_intel_mcp.tools.answer import answer_with_citations
from doc_intel_mcp.tools.documents import list_documents, read_chunk
from doc_intel_mcp.tools.search import search_documents

mcp = MCPServer("doc-intel")

mcp.tool()(list_documents)
mcp.tool()(search_documents)
mcp.tool()(read_chunk)
mcp.tool()(answer_with_citations)

if __name__ == "__main__":
    mcp.run(transport="stdio")