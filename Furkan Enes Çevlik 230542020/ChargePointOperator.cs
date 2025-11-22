using System;
using System.Collections.Generic;
using System.Linq;

public class ChargePointOperator
{
    private readonly List<ChargePoint> _chargePoints;
    private readonly List<ChargeSession> _activeSessions;

    public ChargePointOperator(List<ChargePoint> chargePoints)
    {
        _chargePoints = chargePoints;
        _activeSessions = new List<ChargeSession>();
    }

    public ChargeResponse RequestCharge(string userId, string stationId)
    {
        var station = _chargePoints.FirstOrDefault(s => s.StationId == stationId);
        if (station == null)
            return new ChargeResponse { IsSuccess = false, Message = "Hata: İstasyon bulunamadı." };

        if (station.IsInUse)
            return new ChargeResponse { IsSuccess = false, Message = "Hata: İstasyon şu anda meşgul." };

        var existingSession = _activeSessions.FirstOrDefault(s => s.UserId == userId);

        if (existingSession != null)
        {
            string anomalyMessage = $"ANOMALİ TESPİT EDİLDİ: " +
                                $"'{userId}' kimliği zaten '{existingSession.StationId}' " +
                                $"(Konum: {_chargePoints.First(s => s.StationId == existingSession.StationId).Location}) " +
                                $"istasyonunda aktif bir oturuma sahip. " +
                                $"'{stationId}' (Konum: {station.Location}) istasyonundan gelen bu yeni talep " +
                                $"kimlik klonlama şüphesiyle engellendi.";
            
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine(anomalyMessage);
            Console.ResetColor();

            return new ChargeResponse { IsSuccess = false, Message = anomalyMessage };
        }

        station.IsInUse = true;
        var newSession = new ChargeSession
        {
            SessionId = Guid.NewGuid().ToString(),
            UserId = userId,
            StationId = stationId,
            StartTime = DateTime.UtcNow
        };

        _activeSessions.Add(newSession);

        string successMessage = $"BAŞARILI: '{userId}' kimliği ile '{station.StationId}' (Konum: {station.Location}) istasyonunda şarj başlatıldı.";
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine(successMessage);
        Console.ResetColor();

        return new ChargeResponse { IsSuccess = true, Message = successMessage, Session = newSession };
    }

    public void StopCharge(string sessionId)
    {
        var session = _activeSessions.FirstOrDefault(s => s.SessionId == sessionId);
        if (session != null)
        {
            var station = _chargePoints.FirstOrDefault(s => s.StationId == session.StationId);
            if(station != null)
            {
                station.IsInUse = false;
            }
            _activeSessions.Remove(session);
            Console.WriteLine($"DURDURULDU: '{session.UserId}' kimliğinin '{session.StationId}' istasyonundaki oturumu sonlandırıldı.");
        }
    }
}