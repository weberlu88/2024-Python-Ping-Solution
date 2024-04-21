"""
The ping function takes in a list of IP addresses as targets and allows optional parameters to customize ping settings 
such as count, interval, timeout, concurrent_tasks, source, family, and privileged.

Inside the function, we call async_multiping with the provided parameters and return the responses.
We return the responses wrapped in HostResponse objects.

A list of Host objects containing statistics about the desired destinations:
address, min_rtt, avg_rtt, max_rtt, rtts, packets_sent, packets_received, packet_loss, jitter, is_alive
The list is sorted in the same order as the addresses passed in parameters.
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from icmplib import async_multiping


class PingRequest(BaseModel):
    targets: List[str]
    count: int = 2
    interval: float = 0.5
    timeout: float = 2
    concurrent_tasks: int = 50
    source: Optional[str] = None
    family: Optional[str] = None
    privileged: bool = True


class HostResponse(BaseModel):
    address: str
    min_rtt: Optional[float]
    avg_rtt: Optional[float]
    max_rtt: Optional[float]
    rtts: Optional[List[float]]
    packets_sent: Optional[int]
    packets_received: Optional[int]
    packet_loss: Optional[float]
    jitter: Optional[float]
    is_alive: Optional[bool]


class PingResponse(BaseModel):
    execution_time: str
    execution_duration: float
    num_of_address: int
    num_of_address_is_alive: int
    num_of_address_not_alive: int
    details: List[HostResponse]


app = FastAPI()

@app.post("/ping/", response_model=PingResponse)
async def ping(request: PingRequest):
    start_time = datetime.now()
    try:
        responses = await async_multiping(
            addresses=request.targets,
            count=request.count,
            interval=request.interval,
            timeout=request.timeout,
            concurrent_tasks=request.concurrent_tasks,
            source=request.source,
            family=request.family,
            privileged=request.privileged
        )
        end_time = datetime.now()
        execution_duration = (end_time - start_time).total_seconds() * 1000  # in milliseconds
        num_of_address = len(responses)
        num_of_address_is_alive = sum(1 for host in responses if host.is_alive)
        num_of_address_not_alive = num_of_address - num_of_address_is_alive

        return PingResponse(
            execution_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            execution_duration=execution_duration,
            num_of_address=num_of_address,
            num_of_address_is_alive=num_of_address_is_alive,
            num_of_address_not_alive=num_of_address_not_alive,
            details=responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
