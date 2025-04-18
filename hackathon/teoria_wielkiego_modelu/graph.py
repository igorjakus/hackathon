from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from loguru import logger

from .agents.connector import create_connector_agent
from .agents.critique import create_critique_agent
from .agents.devil_advocate import create_devil_advocate_agent
from .agents.experiment_planner import create_experiment_planner_agent
from .agents.experiment_reviewer import create_experiment_reviewer_agent
from .agents.hypothesis_generator import create_hypothesis_generator_agent
from .agents.hypothesis_refiner import create_hypothesis_refiner_agent
from .agents.inspirations import create_inspiration_agent
from .agents.literature import create_literature_agent
from .agents.novelty_and_impact_reviewer import create_nai_agent
from .agents.ontologist import create_ontologist_agent
from .agents.review_agent import create_review_agent
from .agents.summary import create_summary_agent
from .state import HypgenState


def improve_hypothesis(
    state: HypgenState,
) -> Literal["hypothesis_refiner", "summary_agent"]:
    if state["iteration"] > 3:
        logger.info("Iteration limit reached after {} iterations", state["iteration"])
        return "summary_agent"
    if "ACCEPT" in state["critique"]:
        logger.info("Hypothesis accepted after {} iterations", state["iteration"])
        return "summary_agent"
    else:
        logger.info("Hypothesis rejected after {} iterations", state["iteration"])
        return "hypothesis_refiner"

def create_hypgen_graph() -> CompiledGraph:
    graph = StateGraph(HypgenState)

    # Add nodes with specialized agents
    graph.add_node("ontologist", create_ontologist_agent("small")["agent"])
    graph.add_node("connector", create_connector_agent("small")["agent"])
    graph.add_node(
        "hypothesis_generator", create_hypothesis_generator_agent("small")["agent"]
    )
    graph.add_node(
        "hypothesis_refiner", create_hypothesis_refiner_agent("small")["agent"]
    )
    graph.add_node("literature_agent", create_literature_agent("small")["agent"])
    graph.add_node("inspiration_agent", create_inspiration_agent("small")["agent"])
    graph.add_node("nai_agent", create_nai_agent("small")["agent"])
    graph.add_node("exp_planer", create_experiment_planner_agent("small")["agent"])
    graph.add_node("exp_reviewer", create_experiment_reviewer_agent("small")["agent"])
    graph.add_node("critique_analyst", create_critique_agent("small")["agent"])
    graph.add_node("devil_advocate", create_devil_advocate_agent("small")["agent"])
    graph.add_node("summary_agent", create_summary_agent("small")["agent"])
    
    graph.add_node("review_agent", create_review_agent("small")["agent"])

    # Add edges
    graph.add_edge(START, "ontologist")
    graph.add_edge("ontologist","connector")
    graph.add_edge("connector", "inspiration_agent")
    graph.add_edge("inspiration_agent", "hypothesis_generator")
    # From initial hypothesis
    graph.add_edge("hypothesis_generator", "hypothesis_refiner")
    # From refined hypothesis
    graph.add_edge("hypothesis_refiner", "literature_agent")
    # # Fork
    graph.add_edge("literature_agent", "nai_agent")
    graph.add_edge("nai_agent", "exp_planer")
    graph.add_edge("exp_planer", "exp_reviewer")
    # # Join
    # graph.add_edge("nai_agent", "critique_analyst")
    # graph.add_edge("nai_agent", "devil_advocate")

    # graph.add_edge("exp_planer", "critique_analyst")
    # graph.add_edge("exp_planer", "devil_advocate")

    graph.add_edge("exp_reviewer", "critique_analyst")
    graph.add_edge("critique_analyst", "devil_advocate")
    graph.add_edge("devil_advocate", "review_agent")
    graph.add_edge("review_agent", "summary_agent")
    
    graph.add_edge("summary_agent", END)

    return graph.compile()

def create_refine_graph() -> CompiledGraph:
    graph = StateGraph(HypgenState)

    graph.add_node(
        "hypothesis_refiner", create_hypothesis_refiner_agent("small")["agent"]
    )
    graph.add_node("literature_agent", create_literature_agent("small")["agent"])
    graph.add_node("inspiration_agent", create_inspiration_agent("small")["agent"])
    graph.add_node("nai_agent", create_nai_agent("small")["agent"])
    graph.add_node("exp_planer", create_experiment_planner_agent("small")["agent"])
    graph.add_node("exp_reviewer", create_experiment_reviewer_agent("small")["agent"])
    graph.add_node("critique_analyst", create_critique_agent("small")["agent"])
    graph.add_node("devil_advocate", create_devil_advocate_agent("small")["agent"])
    graph.add_node("summary_agent", create_summary_agent("small")["agent"])
    
    graph.add_node("review_agent", create_review_agent("small")["agent"])

    # Add edges
    graph.add_edge(START, "hypothesis_refiner")

    graph.add_edge("hypothesis_refiner", "literature_agent")
    # # Fork
    graph.add_edge("literature_agent", "nai_agent")
    graph.add_edge("literature_agent", "exp_planer")
    graph.add_edge("exp_planer", "exp_reviewer")
    # # Join
    graph.add_edge("nai_agent", "critique_analyst")
    graph.add_edge("nai_agent", "devil_advocate")

    graph.add_edge("exp_planer", "critique_analyst")
    graph.add_edge("exp_planer", "devil_advocate")

    graph.add_edge("exp_reviewer", "critique_analyst")
    graph.add_edge("exp_reviewer", "devil_advocate")

    graph.add_edge("critique_analyst", "review_agent")
    graph.add_edge("devil_advocate", "review_agent")
    graph.add_edge("review_agent", "summary_agent")
    
    graph.add_edge("summary_agent", END)

    return graph.compile()


seeding_graph = create_hypgen_graph()
refine_graph = create_refine_graph()