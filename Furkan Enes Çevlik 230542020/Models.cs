using System;
using System.Collections.Generic;
using System.Linq;

public class ChargePoint
{
    public string StationId { get; set; }
    public string Location { get; set; }
    public bool IsInUse { get; set; } = false;
}

public class ChargeSession
{
    public string SessionId { get; set; }
    public string UserId { get; set; }
    public string StationId { get; set; }
    public DateTime StartTime { get; set; }
}

public class ChargeResponse
{
    public bool IsSuccess { get; set; }
    public string Message { get; set; }
    public ChargeSession? Session { get; set; }
}