// See https://aka.ms/new-console-template for more information


int[,] Cross(int[,] a, int[,] b)
{
    return a;
}

int[,] GenerateWeights()
{
    var res = new int[4,4];
    return res;
}

async Task<int> NewJob()
{
    return await Task.Run(() =>
        {
            Console.WriteLine("Hello, World!");
            var path = @"C:\Users\Clover\Desktop\AI\Reversi\reversi.py";
            var eng = IronPython.Hosting.Python.CreateEngine();
            var scope = eng.CreateScope();
            return eng.Execute<int>(File.ReadAllText(path));
        });
}

