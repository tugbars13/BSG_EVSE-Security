public class Program
{
    public static void Main(string[] args)
    {
        var stations = new List<ChargePoint>
        {
            new ChargePoint { StationId = "IST-001", Location = "İstanbul" },
            new ChargePoint { StationId = "ANK-002", Location = "Ankara" }
        };
        var cpo = new ChargePointOperator(stations);

        string legitUserId = "RFID-AHMET-12345";
        string clonedUserId = "RFID-AHMET-12345";

        Console.WriteLine("--- TEST BAŞLANGICI ---");
        Console.WriteLine($"Meşru Kullanıcı ID: {legitUserId}");
        Console.WriteLine($"Klonlanmış ID: {clonedUserId}");
        Console.WriteLine(new string('-', 25));

        Console.WriteLine("\n[SENARYO 1: MEŞRU KULLANIM]");
        Console.WriteLine("Ahmet, İstanbul'daki (IST-001) istasyonda şarj başlatıyor...");

        var response1 = cpo.RequestCharge(legitUserId, "IST-001");
        Console.WriteLine($"Yanıt: {response1.Message}\n");

        if (!response1.IsSuccess)
        {
            Console.WriteLine("Meşru kullanım başarısız oldu, test durduruldu.");
            return;
        }

        Console.WriteLine(new string('-', 25));

        Console.WriteLine("\n[SENARYO 2: KİMLİK KLONLAMA ANOMALİSİ]");
        Console.WriteLine("Ahmet İstanbul'da şarjdayken, kötü niyetli bir kişi Ahmet'in");
        Console.WriteLine($"klonlanmış kimliği ({clonedUserId}) ile Ankara'daki (ANK-002) istasyonda şarj başlatmayı deniyor...");

        var response2 = cpo.RequestCharge(clonedUserId, "ANK-002");

        Console.WriteLine(new string('-', 25));

        Console.WriteLine("\n[TEMİZLİK]");
        Console.WriteLine("Ahmet, İstanbul'daki (IST-001) şarjını bitiriyor...");
        if(response1.Session != null)
        {
            cpo.StopCharge(response1.Session.SessionId);
        }

        Console.WriteLine(new string('-', 25));

        Console.WriteLine("\n[SENARYO 3: MEŞRU KULLANIMIN DEVAMI]");
        Console.WriteLine("Kötü niyetli kişinin denemesi engellendikten ve Ahmet'in ilk şarjı bittikten sonra,");
        Console.WriteLine("Ahmet (meşru kullanıcı) Ankara'ya (ANK-002) gidip tekrar şarj başlatmayı deniyor...");

        var response3 = cpo.RequestCharge(legitUserId, "ANK-002");
        Console.WriteLine($"Yanıt: {response3.Message}\n");

        Console.WriteLine("--- TEST SONU ---");
    }
}