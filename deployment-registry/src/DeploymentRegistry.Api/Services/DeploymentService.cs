using DeploymentRegistry.Api.Configuration;
using DeploymentRegistry.Api.Models;
using Microsoft.Extensions.Options;
using MongoDB.Driver;

namespace DeploymentRegistry.Api.Services;

public class DeploymentService : IDeploymentService
{
    private readonly IMongoCollection<Deployment> _deployments;

    public DeploymentService(IOptions<MongoDbSettings> settings)
    {
        var client = new MongoClient(settings.Value.ConnectionString);
        var database = client.GetDatabase(settings.Value.DatabaseName);
        _deployments = database.GetCollection<Deployment>(settings.Value.CollectionName);
    }

    public async Task<List<Deployment>> GetAsync(string? serviceName, string? environment, string? status)
    {
        var builder = Builders<Deployment>.Filter;
        var filter = builder.Empty;

        if (!string.IsNullOrEmpty(serviceName))
            filter &= builder.Eq(d => d.ServiceName, serviceName);

        if (!string.IsNullOrEmpty(environment))
            filter &= builder.Eq(d => d.Environment, environment);

        if (!string.IsNullOrEmpty(status))
            filter &= builder.Eq(d => d.Status, status);

        return await _deployments.Find(filter).SortByDescending(d => d.StartedAt).ToListAsync();
    }

    public async Task<Deployment?> GetByIdAsync(string id)
    {
        return await _deployments.Find(d => d.Id == id).FirstOrDefaultAsync();
    }

    public async Task<Deployment> CreateAsync(Deployment deployment)
    {
        await _deployments.InsertOneAsync(deployment);
        return deployment;
    }

    public async Task<Deployment?> UpdateAsync(string id, Deployment deployment)
    {
        // NOTE: This intentionally does NO validation on field consistency.
        // It blindly replaces the document with whatever the caller sends.
        // For example, it does not check whether FinishedAt is set appropriately
        // for the given Status value.
        var result = await _deployments.ReplaceOneAsync(d => d.Id == id, deployment);
        if (result.MatchedCount == 0)
            return null;
        return deployment;
    }
}
